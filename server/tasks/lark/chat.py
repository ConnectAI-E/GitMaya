import json
import logging

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
from utils.github.repo import GitHubAppRepo
from utils.lark.chat_manual import ChatManual, ChatView
from utils.lark.chat_tip_failed import ChatTipFailed
from utils.lark.issue_card import IssueCard
from utils.lark.post_message import post_content_to_markdown

from .base import (
    get_bot_by_application_id,
    get_chat_group_by_chat_id,
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
            Repo.id == chat_group.repo_id,
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
        return send_chat_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
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
        return send_chat_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
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
            "issue 标题为空", app_id, message_id, content, data, *args, bot=bot, **kwargs
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
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == chat_group.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    if not repo:
        return send_chat_failed_tip(
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
    # 当前操作的用户
    current_code_user_id = code_users[openid][0]

    github_app = GitHubAppRepo(
        code_application.installation_id, user_id=current_code_user_id
    )
    assignees = [code_users[openid][1] for openid in users if openid in code_users]
    response = github_app.create_issue(
        team.name, repo.name, title, body, assignees, labels
    )
    if "id" not in response:
        return send_chat_failed_tip(
            "创建 issue 失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response
