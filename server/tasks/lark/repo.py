import logging

from connectai.lark.sdk import Bot
from lark import get_bot_by_application_id
from sqlalchemy import func, or_

from celery_app import app, celery
from model.schema import (
    BindUser,
    ChatGroup,
    CodeApplication,
    IMApplication,
    ObjID,
    Repo,
    Team,
    User,
    db,
)
from utils.lark.repo_manual import RepoManual
from utils.lark.repo_tip_failed import RepoTipFailed
from utils.lark.repo_tip_success import RepoTipSuccess


@celery.task()
def send_repo_failed_tip(content, app_id, message_id, *args, bot=None, **kwargs):
    """send a new repo failed tip to user.
    Args:
        content (str): The error message to be sent.
        app_id (str): The ID of the IM application.
        message_id (str): The ID of the Lark message.
        *args: Additional positional arguments.
        bot (Bot, optional): The bot instance. Defaults to None.
        **kwargs: Additional keyword arguments.
    Returns:
        dict: The JSON response from the bot's reply method.
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = RepoTipFailed(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_repo_manual(app_id, message_id, repo_id, *args, **kwargs):
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = RepoManual()
    return bot.reply(message_id, message).json()


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
