import logging
from email import message

from celery_app import app, celery
from connectai.lark.sdk import Bot
from lark import get_bot_by_application_id
from model.schema import (
    BindUser,
    ChatGroup,
    CodeApplication,
    ErrorMsg,
    IMApplication,
    ObjID,
    Repo,
    SuccessMsg,
    Team,
    User,
    db,
)
from sqlalchemy import func, or_
from utils.lark.repo_info import RepoInfo
from utils.lark.repo_manual import RepoManual
from utils.lark.repo_tip_failed import RepoTipFailed
from utils.lark.repo_tip_success import RepoTipSuccess


def get_repo_id_by_chat_group(chat_id):
    chat_group = (
        db.session.query(ChatGroup)
        .filter(
            ChatGroup.chat_id == chat_id,
            ChatGroup.status == 0,
        )
        .first()
    )

    return chat_group


def get_repo_name_by_repo_id(repo_id):
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
            Repo.status == 0,
        )
        .first()
    )
    return repo.name


@celery.task()
def get_repo_url_by_chat_id(chat_id, *args, **kwargs):
    chat_group = get_repo_id_by_chat_group(chat_id)

    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == chat_group.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    team = (
        db.session.query(Team)
        .filter(
            Team.id == chat_group.team_id,
            Team.status == 0,
        )
        .first()
    )
    return f"https://github.com/{team.name}/{repo.name}"


@celery.task()
def send_repo_failed_tip(content, app_id, message_id, *args, bot=None, **kwargs):
    """send a new repo failed tip to user.
    Args:
        content (str): The error message to be sent.
        app_id (str): The ID of the IM application.
        message_id (str): The ID of the Lark message.
        bot (Bot, optional): The bot instance. Defaults to None.
    Returns:
        dict: The JSON response from the bot's reply method.
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = RepoTipFailed(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_repo_success_tip(content, app_id, message_id, *args, bot=None, **kwargs):
    """send new repo success tip to user.

    Args:
        content (str): The success message to be sent.
        app_id (str): The ID of the IMApplication.
        message_id (str): The ID of the lark message.
        bot (Bot, optional): The bot instance. Defaults to None.

    Returns:
        dict: The JSON response from the bot's reply method.
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = RepoTipSuccess()(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_repo_manual(app_id, message_id, data, *args, **kwargs):
    """
    Send repository manual to a chat group.

    Args:
        app_id (int): The ID of the application.
        message_id (int): The ID of the message.
        data (dict): The data containing the event message and chat ID.

    Returns:
        dict: The JSON response from the bot.

    """
    bot, application = get_bot_by_application_id(app_id)

    # 通过chat_group查repo id
    chat_group = get_repo_id_by_chat_group(data)
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == chat_group.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    if repo:
        team = (
            db.session.query(Team)
            .filter(
                Team.id == application.team_id,
            )
            .first()
        )
        message = RepoManual(
            repo_url=f"https://github.com/{team.name}/{repo.name}",
            repo_name=repo.name,
            repo_description=repo.description,
            visibility=repo.extra.get("visibility", "public"),
        )
    return bot.reply(message_id, message).json()


@celery.task()
def send_repo_info(app_id, chat_group_id, repo_id, *args, **kwargs):
    bot, application = get_bot_by_application_id(app_id)

    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )

    if repo:
        bot, application = get_bot_by_application_id(app_id)
        team = (
            db.session.query(Team)
            .filter(
                Team.id == application.team_id,
            )
            .first()
        )
        # TODO 获取 repo 信息
        message = RepoInfo(
            repo_url=f"https://github.com/{team.name}/{repo.name}",
            repo_name=repo.name,
            repo_description=repo.description,
            repo_topic=repo.extra.get("topic", []),
            open_issues_count=4,
            stargazers_count=5,
            forks_count=6,
            visibility="私有仓库" if repo.extra.get("private") else "公开仓库",
        )
        return bot.send(
            chat_group_id,
            message,
            receive_id_type="chat_id",
        ).json()
    return bot.reply(chat_group_id, message).json()


def process_repo_action(
    app_id, message_id, repo_id, action, param=None, *args, **kwargs
):
    """处理 Repo 操作"""
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    # 操作github
    result = None
    if action == "rename":
        result = github_rename_repo(repo_id, param, *args, **kwargs)
    elif action == "edit":
        result = github_edit_repo(repo_id, param, *args, **kwargs)
    elif action == "link":
        result = github_link_repo(repo_id, param, *args, **kwargs)
    elif action == "label":
        result = github_label_repo(repo_id, param, *args, **kwargs)

    if result and result["result"] == "success":
        message = RepoTipSuccess(result["text"])
    elif result and result["result"] == "failed":
        message = RepoTipFailed(result["text"])
    return bot.reply(message_id, message).json()


@celery.task()
def rename_repo(app_id, message_id, repo_id, param, *args, **kwargs):
    """修改 Repo 标题"""
    return process_repo_action(
        app_id, message_id, repo_id, "rename", param, *args, **kwargs
    )


@celery.task()
def edit_repo(app_id, message_id, repo_id, param, *args, **kwargs):
    """编辑 Repo"""
    return process_repo_action(
        app_id, message_id, repo_id, "edit", param, *args, **kwargs
    )


@celery.task()
def link_repo(app_id, message_id, repo_id, param, *args, **kwargs):
    """关联 Repo"""
    return process_repo_action(
        app_id, message_id, repo_id, "link", param, *args, **kwargs
    )


@celery.task()
def label_repo(app_id, message_id, repo_id, param, *args, **kwargs):
    """标记 Repo"""
    return process_repo_action(
        app_id, message_id, repo_id, "label", param, *args, **kwargs
    )
