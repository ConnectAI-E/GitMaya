import json
import logging
import re

from celery_app import app, celery
from connectai.lark.sdk import FeishuTextMessage
from model.schema import (
    ChatGroup,
    CodeApplication,
    CodeUser,
    IMUser,
    Issue,
    Repo,
    Team,
    TeamMember,
    db,
)
from model.team import get_assignees_by_openid
from utils.github.repo import GitHubAppRepo
from utils.lark.issue_card import IssueCard
from utils.lark.issue_manual_help import IssueManualHelp, IssueView
from utils.lark.issue_tip_failed import IssueTipFailed
from utils.lark.issue_tip_success import IssueTipSuccess

from .base import (
    get_bot_by_application_id,
    get_git_object_by_message_id,
    with_authenticated_github,
)


@celery.task()
def send_issue_failed_tip(content, app_id, message_id, *args, bot=None, **kwargs):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: error message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = IssueTipFailed(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_issue_success_tip(content, app_id, message_id, *args, bot=None, **kwargs):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: success message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = IssueTipSuccess(content=content)
    return bot.reply(message_id, message).json()


def get_assignees_by_issue(issue, team):
    assignees = issue.extra.get("assignees", [])
    if len(assignees):
        assignees = [
            openid
            for openid, in db.session.query(IMUser.openid)
            .join(TeamMember, TeamMember.im_user_id == IMUser.id)
            .join(
                CodeUser,
                CodeUser.id == TeamMember.code_user_id,
            )
            .filter(
                TeamMember.team_id == team.id,
                CodeUser.name.in_([i["login"] for i in assignees]),
            )
            .all()
        ]
    return assignees


def gen_issue_card_by_issue(issue, repo_url, team, maunal=False):
    assignees = get_assignees_by_issue(issue, team)
    tags = [i["name"] for i in issue.extra.get("labels", [])]
    status = issue.extra.get("state", "opened")
    if status == "closed":
        status = "已关闭"
    else:
        status = "待完成"

    if maunal:
        return IssueManualHelp(
            repo_url=repo_url,
            issue_id=issue.issue_number,
            # TODO 这里需要找到真实的值
            # persons=[],
            status=status,
            assignees=assignees,
            tags=tags,
        )

    return IssueCard(
        repo_url=repo_url,
        id=issue.issue_number,
        title=issue.title,
        description=issue.description,
        status=status,
        assignees=assignees,
        tags=tags,
        updated=issue.modified.strftime("%Y-%m-%d %H:%M:%S"),
    )


def send_issue_url_message(
    app_id, message_id, content, data, *args, typ="view", **kwargs
):
    root_id = data["event"]["message"]["root_id"]
    _, issue, _ = get_git_object_by_message_id(root_id)
    if not issue:
        return send_issue_failed_tip(
            "找不到 Issue", app_id, message_id, content, data, *args, **kwargs
        )
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == issue.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    if not issue:
        return send_issue_failed_tip(
            "找不到项目", app_id, message_id, content, data, *args, **kwargs
        )
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_issue_failed_tip(
            "找不到对应的应用", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == application.team_id,
        )
        .first()
    )
    if not team:
        return send_issue_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    repo_url = f"https://github.com/{team.name}/{repo.name}"
    if "view" == typ:
        message = IssueView(
            repo_url=repo_url,
            issue_id=issue.issue_number,
        )
    else:
        return send_issue_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )
    # 回复到话题内部
    return bot.reply(message_id, message).json()


@celery.task()
def send_issue_view_message(app_id, message_id, content, data, *args, **kwargs):
    return send_issue_url_message(
        app_id, message_id, content, data, *args, typ="view", **kwargs
    )


@celery.task()
def send_issue_manual(app_id, message_id, content, data, *args, **kwargs):
    root_id = data["event"]["message"]["root_id"]
    _, issue, _ = get_git_object_by_message_id(root_id)
    if not issue:
        return send_issue_failed_tip(
            "找不到 Issue", app_id, message_id, content, data, *args, **kwargs
        )
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == issue.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    if not repo:
        return send_issue_failed_tip(
            "找不到项目", app_id, message_id, content, data, *args, **kwargs
        )
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_issue_failed_tip(
            "找不到对应的应用", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == application.team_id,
        )
        .first()
    )
    if not team:
        return send_issue_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    repo_url = f"https://github.com/{team.name}/{repo.name}"
    message = gen_issue_card_by_issue(issue, repo_url, team, True)
    # 回复到话题内部
    return bot.reply(message_id, message).json()


@celery.task()
def send_issue_card(issue_id):
    """send new issue card message to user.

    Args:
        issue_id: Issue.id.
    """
    issue = db.session.query(Issue).filter(Issue.id == issue_id).first()
    if issue:
        chat_group = (
            db.session.query(ChatGroup)
            .filter(
                ChatGroup.repo_id == issue.repo_id,
            )
            .first()
        )
        repo = db.session.query(Repo).filter(Repo.id == issue.repo_id).first()
        if chat_group and repo:
            bot, application = get_bot_by_application_id(chat_group.im_application_id)
            team = db.session.query(Team).filter(Team.id == application.team_id).first()
            if application and team:
                repo_url = f"https://github.com/{team.name}/{repo.name}"
                message = gen_issue_card_by_issue(issue, repo_url, team)
                result = bot.send(
                    chat_group.chat_id, message, receive_id_type="chat_id"
                ).json()
                message_id = result.get("data", {}).get("message_id")
                if message_id:
                    # save message_id
                    issue.message_id = message_id
                    db.session.commit()

                    assignees = get_assignees_by_issue(issue, team)
                    users = (
                        "".join(
                            [f'<at user_id="{open_id}"></at>' for open_id in assignees]
                        )
                        if len(assignees)
                        else ""
                    )
                    first_message_result = bot.reply(
                        message_id,
                        # 第一条话题消息，直接放repo_url
                        FeishuTextMessage(
                            users + f"{repo_url}/issues/{issue.issue_number}"
                        ),
                        reply_in_thread=True,
                    ).json()
                    logging.info("debug first_message_result %r", first_message_result)
                return result
    return False


@celery.task()
def send_issue_comment(issue_id, comment, user_name: str):
    """send new issue comment message to user.

    Args:
        issue_id: Issue.id.
        comment: str
    """
    issue = db.session.query(Issue).filter(Issue.id == issue_id).first()
    if issue:
        chat_group = (
            db.session.query(ChatGroup)
            .filter(
                ChatGroup.repo_id == issue.repo_id,
            )
            .first()
        )
        if chat_group and issue.message_id:
            bot, _ = get_bot_by_application_id(chat_group.im_application_id)
            result = bot.reply(
                issue.message_id,
                FeishuTextMessage(f"@{user_name}: {comment}"),
            ).json()
            return result
    return False


@celery.task()
def update_issue_card(issue_id: str):
    """Update issue card message.

    Args:
        issue_id (str): Issue.id.
    """

    issue = db.session.query(Issue).filter(Issue.id == issue_id).first()
    if issue:
        chat_group = (
            db.session.query(ChatGroup)
            .filter(
                ChatGroup.repo_id == issue.repo_id,
            )
            .first()
        )
        repo = db.session.query(Repo).filter(Repo.id == issue.repo_id).first()

        if chat_group and repo:
            bot, application = get_bot_by_application_id(chat_group.im_application_id)
            team = db.session.query(Team).filter(Team.id == application.team_id).first()
            if application and team:
                repo_url = f"https://github.com/{team.name}/{repo.name}"
                message = gen_issue_card_by_issue(issue, repo_url, team)
                result = bot.update(
                    message_id=issue.message_id,
                    content=message,
                )

                return result.json()

    return False


def _get_github_app(app_id, message_id, content, data, *args, **kwargs):
    root_id = data["event"]["message"].get(
        "root_id", data["event"]["message"]["message_id"]
    )
    openid = data["event"]["sender"]["sender_id"]["open_id"]

    _, issue, _ = get_git_object_by_message_id(root_id)
    if not issue:
        return send_issue_failed_tip(
            "找不到 Issue", app_id, message_id, content, data, *args, **kwargs
        )
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == issue.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    if not repo:
        return send_issue_failed_tip(
            "找不到项目", app_id, message_id, content, data, *args, **kwargs
        )

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.id == repo.application_id,
        )
        .first()
    )
    if not code_application:
        return send_issue_failed_tip(
            "找不到对应的应用", app_id, message_id, content, data, *args, **kwargs
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == code_application.team_id,
        )
        .first()
    )
    if not team:
        return send_issue_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, **kwargs
        )

    code_user_id = (
        db.session.query(CodeUser.user_id)
        .join(
            TeamMember,
            TeamMember.code_user_id == CodeUser.id,
        )
        .join(
            IMUser,
            IMUser.id == TeamMember.im_user_id,
        )
        .filter(
            IMUser.openid == openid,
            TeamMember.team_id == team.id,
        )
        .limit(1)
        .scalar()
    )

    github_app = GitHubAppRepo(code_application.installation_id, user_id=code_user_id)
    return github_app, team, repo, issue, root_id, openid


@celery.task()
@with_authenticated_github()
def create_issue_comment(app_id, message_id, content, data, *args, **kwargs):
    github_app, team, repo, issue, _, _ = _get_github_app(
        app_id, message_id, content, data, *args, **kwargs
    )
    comment_text = content["text"]

    # 判断 content 中是否有 at
    if "mentions" in data["event"]["message"]:
        # 获得 mentions 中的 openid list
        mentions = data["event"]["message"]["mentions"]
        openid_list = [mention["id"]["open_id"] for mention in mentions]
        code_name_list = []

        for openid in openid_list:
            # 通过 openid list 获得 code_name_list
            code_name_list.append(
                get_github_name_by_openid(
                    openid,
                    team.id,
                    app_id,
                    message_id,
                    content,
                    data,
                    *args,
                    **kwargs,
                )
            )

        # 替换 content 中的 im_name 为 code_name
        comment_text = replace_im_name_to_github_name(content["text"], code_name_list)

    response = github_app.create_issue_comment(
        team.name, repo.name, issue.issue_number, comment_text
    )
    if "id" not in response:
        return send_issue_failed_tip(
            "同步消息失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response


def replace_im_name_to_github_name(content, code_name_list):
    """
    replace im name to github name

    Args:
        content (str): content
        code_name_list (list): code name list

    Returns:
        str: replaced content
    """

    # 替换函数
    def replace_user(match):
        index = int(match.group(1)) - 1  # 获取用户编号并转换为索引
        return (
            f"@{code_name_list[index]}"
            if 0 <= index < len(code_name_list)
            else match.group(0)
        )

    return re.sub(r"@_user_(\d+)", replace_user, content)


def get_github_name_by_openid(
    openid, team_id, app_id, message_id, content, data, *args, **kwargs
):
    """
    get github name by openid

    Args:
        openid (str): openid
        team_id (str): team_id
        app_id (str): app_id
        message_id (str): message_id
        content (str): content
        data (dict): data

    Returns:
        str: GitHub name
    """
    # 第一步：根据 openid 和 team_id 查询 team_member 表得到 im_user_id
    im_user_id = (
        db.session.query(TeamMember.im_user_id)
        .join(
            IMUser,  # BindUser 表是 CodeUser 和 IMUser 的别名
            IMUser.id == TeamMember.im_user_id,
        )
        .filter(
            IMUser.openid == openid,
            TeamMember.team_id == team_id,
        )
        .limit(1)
        .scalar()
    )

    if not im_user_id:
        return send_issue_failed_tip(
            "找不到对应的飞书用户", app_id, message_id, content, data, *args, **kwargs
        )

    # 第二步：使用 im_user_id 和 team_id 再次查询 team_member 表得到 code_user_id
    code_user_id = (
        db.session.query(TeamMember.code_user_id)
        .filter(
            TeamMember.im_user_id == im_user_id,
            TeamMember.team_id == team_id,
        )
        .limit(1)
        .scalar()
    )

    if not code_user_id:
        return send_issue_failed_tip(
            "找不到对应的 GitHub 用户", app_id, message_id, content, data, *args, **kwargs
        )

    # 第三步：如果找到了 code_user_id，使用它在 bind_user 表中查询 name
    name = db.session.query(CodeUser.name).filter(CodeUser.id == code_user_id).scalar()

    return name


@celery.task()
@with_authenticated_github()
def close_issue(app_id, message_id, content, data, *args, **kwargs):
    github_app, team, repo, issue, root_id, _ = _get_github_app(
        app_id, message_id, content, data, *args, **kwargs
    )
    response = github_app.update_issue(
        team.name,
        repo.name,
        issue.issue_number,
        state="closed",
    )
    if "id" not in response:
        return send_issue_failed_tip(
            "关闭 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    else:
        send_issue_success_tip(
            "关闭 issue 成功", app_id, message_id, content, data, *args, **kwargs
        )
    # maunal点按钮，需要更新maunal
    if root_id != message_id:
        repo_url = f"https://github.com/{team.name}/{repo.name}"
        issue.extra.update(state="closed")
        message = gen_issue_card_by_issue(issue, repo_url, team, True)
        bot, _ = get_bot_by_application_id(app_id)
        bot.update(message_id=message_id, content=message)
    return response


@celery.task()
@with_authenticated_github()
def reopen_issue(app_id, message_id, content, data, *args, **kwargs):
    github_app, team, repo, issue, root_id, _ = _get_github_app(
        app_id, message_id, content, data, *args, **kwargs
    )
    response = github_app.update_issue(
        team.name,
        repo.name,
        issue.issue_number,
        state="opened",
    )
    if "id" not in response:
        return send_issue_failed_tip(
            "打开 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    else:
        send_issue_success_tip(
            "打开 issue 成功", app_id, message_id, content, data, *args, **kwargs
        )
    # maunal点按钮，需要更新maunal
    if root_id != message_id:
        repo_url = f"https://github.com/{team.name}/{repo.name}"
        issue.extra.update(state="opened")
        message = gen_issue_card_by_issue(issue, repo_url, team, True)
        bot, _ = get_bot_by_application_id(app_id)
        bot.update(message_id=message_id, content=message)
    return response


@celery.task()
@with_authenticated_github()
def change_issue_title(title, app_id, message_id, content, data, *args, **kwargs):
    github_app, team, repo, issue, _, _ = _get_github_app(
        app_id, message_id, content, data, *args, **kwargs
    )
    response = github_app.update_issue(
        team.name,
        repo.name,
        issue.issue_number,
        title=title,
    )
    if "id" not in response:
        return send_issue_failed_tip(
            "更新 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    else:
        send_issue_success_tip(
            "更新 issue 成功", app_id, message_id, content, data, *args, **kwargs
        )
    return response


@celery.task()
@with_authenticated_github()
def change_issue_label(labels, app_id, message_id, content, data, *args, **kwargs):
    github_app, team, repo, issue, _, _ = _get_github_app(
        app_id, message_id, content, data, *args, **kwargs
    )
    response = github_app.update_issue(
        team.name,
        repo.name,
        issue.issue_number,
        labels=labels,
    )
    if "id" not in response:
        return send_issue_failed_tip(
            "更新 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    else:
        send_issue_success_tip(
            "更新 issue 成功", app_id, message_id, content, data, *args, **kwargs
        )
    return response


@celery.task()
@with_authenticated_github()
def change_issue_desc(desc, app_id, message_id, content, data, *args, **kwargs):
    github_app, team, repo, issue, _, _ = _get_github_app(
        app_id, message_id, content, data, *args, **kwargs
    )
    response = github_app.update_issue(
        team.name,
        repo.name,
        issue.issue_number,
        body=desc,
    )
    if "id" not in response:
        return send_issue_failed_tip(
            "更新 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    else:
        send_issue_success_tip(
            "更新 issue 成功", app_id, message_id, content, data, *args, **kwargs
        )
    return response


@celery.task()
@with_authenticated_github()
def change_issue_assignees(users, app_id, message_id, content, data, *args, **kwargs):
    github_app, team, repo, issue, _, _ = _get_github_app(
        app_id, message_id, content, data, *args, **kwargs
    )
    assignees = get_assignees_by_openid(users)
    if len(assignees) == 0:
        return send_issue_failed_tip(
            "更新 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    response = github_app.update_issue(
        team.name,
        repo.name,
        issue.issue_number,
        assignees=assignees,
    )
    if "id" not in response:
        return send_issue_failed_tip(
            "更新 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    else:
        assignees_name = "、".join(assignees)
        send_issue_success_tip(
            f"已成功将 issue #{issue.issue_number} 负责人修改为 「{assignees_name}」",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )
    return response


@celery.task()
@with_authenticated_github()
def pin_issue(app_id, message_id, content, data, *args, **kwargs):
    # TODO 未找到pin相关API
    return send_issue_failed_tip(
        "更新 issue 失败", app_id, message_id, content, data, *args, **kwargs
    )
