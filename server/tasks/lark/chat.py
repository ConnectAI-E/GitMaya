import json
import logging
from urllib.parse import urlparse

from celery_app import app, celery
from model.schema import (
    ChatGroup,
    CodeApplication,
    CodeUser,
    IMUser,
    Repo,
    Team,
    TeamMember,
    db,
)
from model.team import get_code_users_by_openid
from sqlalchemy.orm import aliased
from tasks.lark.issue import replace_im_name_to_github_name
from utils.github.repo import GitHubAppRepo
from utils.lark.chat_manual import ChatManual, ChatView
from utils.lark.chat_tip_failed import ChatTipFailed
from utils.lark.issue_card import IssueCard
from utils.lark.post_message import post_content_to_markdown

from .base import (
    get_bot_by_application_id,
    get_chat_group_by_chat_id,
    get_git_object_by_message_id,
    get_repo_name_by_repo_id,
    with_authenticated_github,
)


@celery.task()
def send_chat_failed_tip(content, app_id, message_id, *args, bot=None, **kwargs):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: error message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = ChatTipFailed(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_chat_manual(app_id, message_id, content, data, *args, **kwargs):
    chat_id = data["event"]["message"]["chat_id"]
    chat_group = (
        db.session.query(ChatGroup)
        .filter(
            ChatGroup.chat_id == chat_id,
            ChatGroup.status == 0,
        )
        .first()
    )
    if not chat_group:
        return send_chat_failed_tip(
            "找不到项目群", app_id, message_id, content, data, *args, **kwargs
        )
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.chat_group_id == chat_group.id,
            Repo.status == 0,
        )
        .first()
    )
    if not repo:
        return send_chat_failed_tip(
            "找不到项目群", app_id, message_id, content, data, *args, **kwargs
        )
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_chat_failed_tip(
            "找不到对应的应用",
            app_id,
            message_id,
            content,
            data,
            *args,
            bot=bot,
            **kwargs,
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == application.team_id,
        )
        .first()
    )
    if not team:
        return send_chat_failed_tip(
            "找不到对应的项目",
            app_id,
            message_id,
            content,
            data,
            *args,
            bot=bot,
            **kwargs,
        )

    message = ChatManual(
        repo_url=f"https://github.com/{team.name}/{repo.name}",
        repo_name=repo.name,
        actions=[],  # TODO 获取actions
    )
    return bot.reply(message_id, message).json()


def send_chat_url_message(
    app_id, message_id, content, data, *args, typ="view", **kwargs
):
    chat_id = data["event"]["message"]["chat_id"]
    chat_group = get_chat_group_by_chat_id(chat_id)
    repo_name = get_repo_name_by_repo_id(chat_group.repo_id)
    # TODO repo_name可能为空
    # if not repo:
    #     return send_chat_failed_tip(
    #         "找不到Repo", app_id, message_id, content, data, *args, **kwargs
    #     )
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_chat_failed_tip(
            "找不到对应的应用",
            app_id,
            message_id,
            content,
            data,
            *args,
            bot=bot,
            **kwargs,
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == application.team_id,
        )
        .first()
    )
    if not team:
        return send_chat_failed_tip(
            "找不到对应的项目",
            app_id,
            message_id,
            content,
            data,
            *args,
            bot=bot,
            **kwargs,
        )

    repo_url = f"https://github.com/{team.name}/{repo_name}"
    if "view" == typ:
        message = ChatView(repo_url=repo_url)
    elif "insight" == typ:
        message = ChatView(repo_url=f"{repo_url}/pulse")
    return bot.reply(message_id, message).json()


@celery.task()
def send_chat_view_message(app_id, message_id, content, data, *args, **kwargs):
    return send_chat_url_message(
        app_id, message_id, content, data, *args, typ="view", **kwargs
    )


@celery.task()
def send_chat_insight_message(app_id, message_id, content, data, *args, **kwargs):
    return send_chat_url_message(
        app_id, message_id, content, data, *args, typ="insight", **kwargs
    )


@celery.task()
@with_authenticated_github()
def create_issue(
    title, users, labels, app_id, message_id, content, data, *args, **kwargs
):
    body = ""
    if not title:
        # 判断是否为 post
        message_type = data["event"]["message"].get("message_type", None)
        if "post" == message_type:
            content, title = post_content_to_markdown(content, False)
            # desc 从 body 第二行开始读取，第一行作为 /issue @user labels 解析
            body = "\n".join(content.split("\n")[1:])

        # 如果title是空的，尝试从parent_message拿到内容
        parent_id = data["event"]["message"].get("parent_id")
        if parent_id:
            bot, _ = get_bot_by_application_id(app_id)
            parent_message_url = f"{bot.host}/open-apis/im/v1/messages/{parent_id}"
            result = bot.get(parent_message_url).json()
            if len(result["data"].get("items", [])) > 0:
                parent_message = result["data"]["items"][0]
                title = json.loads(parent_message["body"]["content"]).get("text")
    if not title:
        return send_chat_failed_tip(
            "issue 标题为空", app_id, message_id, content, data, *args, **kwargs
        )

    chat_id = data["event"]["message"]["chat_id"]
    chat_group = (
        db.session.query(ChatGroup)
        .filter(
            ChatGroup.chat_id == chat_id,
        )
        .first()
    )
    if not chat_group:
        return send_chat_failed_tip(
            "找不到项目群", app_id, message_id, content, data, *args, **kwargs
        )
    repos = []
    try:
        # 如果是在话题内运行命令（repo/issue/pull_request）尝试找到对应的repo
        if len(repos) == 0:
            root_id = data["event"]["message"].get("root_id", "")
            if root_id:
                repo, issue, pr = get_git_object_by_message_id(root_id)
                if repo:
                    repos = [repo]
                elif issue or pr:
                    repo_id = issue.repo_id if issue else pr.repo_id
                    repo = db.session.query(Repo).filter(Repo.id == repo_id).first()
                    if repo:
                        repos = [repo]
    except Exception as e:
        logging.error(e)

    if len(repos) == 0:
        repos = (
            db.session.query(Repo)
            .filter(
                Repo.chat_group_id == chat_group.id,
                Repo.status == 0,
            )
            .all()
        )
    if len(repos) > 1:
        return send_chat_failed_tip(
            "当前群有多个项目，无法唯一确定仓库",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )

    if len(repos) == 0:
        return send_chat_failed_tip(
            "找不到项目", app_id, message_id, content, data, *args, **kwargs
        )

    repo = repos[0]  # 能找到唯一的仓库才执行

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.id == repo.application_id,
        )
        .first()
    )
    if not code_application:
        return send_chat_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, **kwargs
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == code_application.team_id,
        )
        .first()
    )
    if not team:
        return send_chat_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, **kwargs
        )

    openid = data["event"]["sender"]["sender_id"]["open_id"]
    # 这里连三个表查询，所以一次性都查出来
    code_users = get_code_users_by_openid([openid] + users)

    import tasks

    if openid not in code_users:
        host = os.environ.get("DOMAIN")

        return tasks.send_manage_fail_message(
            f"[请点击绑定 GitHub 账号后重试]({host}/api/github/oauth)",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )

    # 当前操作的用户
    current_code_user_id = code_users[openid][0]

    github_app = GitHubAppRepo(
        code_application.installation_id, user_id=current_code_user_id
    )
    assignees = [code_users[openid][1] for openid in users if openid in code_users]

    # 判断 content 中是否有 at
    if "mentions" in data["event"]["message"]:
        # 替换 content 中的 im_name 为 code_name
        body = replace_im_name_to_github_name(
            app_id, message_id, {"text": body}, data, team, *args, **kwargs
        )
        body = body.replace("\n", "\r\n")

    response = github_app.create_issue(
        team.name, repo.name, title, body, assignees, labels
    )
    if "id" not in response:
        return send_chat_failed_tip(
            "创建 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response


@celery.task()
def sync_issue(
    issue_id, issue_link, app_id, message_id, content, data, *args, **kwargs
):
    repo_name = ""
    is_pr = False
    try:
        if not issue_id:
            path = urlparse(issue_link).path
            issue_id = int(path.split("/").pop())
            repo_name = path.split("/")[2]
            is_pr = path.split("/")[3] == "pull"
    except Exception as e:
        logging.error(e)

    if not issue_id:
        return send_chat_failed_tip(
            "找不到issue", app_id, message_id, content, data, *args, **kwargs
        )

    chat_id = data["event"]["message"]["chat_id"]
    chat_group = (
        db.session.query(ChatGroup)
        .filter(
            ChatGroup.chat_id == chat_id,
        )
        .first()
    )
    if not chat_group:
        return send_chat_failed_tip(
            "找不到项目群", app_id, message_id, content, data, *args, **kwargs
        )

    repos = (
        db.session.query(Repo)
        .filter(
            Repo.chat_group_id == chat_group.id,
            Repo.status == 0,
        )
        .all()
    )
    # 如果有多个，尝试从issue_link里面拿到repo_name过滤一下
    if len(repos) > 1 and repo_name:
        repos = [repo for repo in repos if repo.name == repo_name]

    if len(repos) > 1:
        return send_chat_failed_tip(
            "当前群有多个项目，无法唯一确定仓库",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )
    if len(repos) == 0:
        return send_chat_failed_tip(
            "找不到项目", app_id, message_id, content, data, *args, **kwargs
        )

    repo = repos[0]  # 能找到唯一的仓库才执行

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.id == repo.application_id,
        )
        .first()
    )
    if not code_application:
        return send_chat_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, **kwargs
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == code_application.team_id,
        )
        .first()
    )
    if not team:
        return send_chat_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, **kwargs
        )
    openid = data["event"]["sender"]["sender_id"]["open_id"]
    # 这里连三个表查询，所以一次性都查出来
    code_users = get_code_users_by_openid([openid])

    import tasks

    if openid not in code_users:
        host = os.environ.get("DOMAIN")

        return tasks.send_manage_fail_message(
            f"[请点击绑定 GitHub 账号后重试]({host}/api/github/oauth)",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )

    # 当前操作的用户
    current_code_user_id = code_users[openid][0]

    github_app = GitHubAppRepo(
        code_application.installation_id, user_id=current_code_user_id
    )

    # 后面需要插入记录，再发卡片，创建话题
    repository = github_app.get_repo_info_by_name(team.name, repo.name)
    if is_pr:
        pull_request = github_app.get_one_pull_request(team.name, repo.name, issue_id)
        logging.debug("get_one_pull_requrst %r", pull_request)
        return tasks.on_pull_request_opened(
            {
                "action": "opened",
                "sender": pull_request["user"],
                "pull_request": pull_request,
                "repository": repository,
            }
        )
    else:
        issue = github_app.get_one_issue(team.name, repo.name, issue_id)
        logging.debug("get_one_issue %r", issue)
        return tasks.on_issue_opened(
            {
                "action": "opened",
                "sender": issue["user"],
                "issue": issue,
                "repository": repository,
            }
        )

    return send_chat_failed_tip(
        "同步 issue 失败", app_id, message_id, content, data, *args, **kwargs
    )
