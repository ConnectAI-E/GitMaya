import logging
import webbrowser
from email import message

from celery_app import app, celery
from connectai.lark.sdk import Bot
from lark import *
from model.schema import Repo, Team, db
from utils.lark.repo_info import RepoInfo
from utils.lark.repo_manual import RepoManual
from utils.lark.repo_tip_failed import RepoTipFailed
from utils.lark.repo_tip_success import RepoTipSuccess

from .base import *


@celery.task()
def get_repo_url_by_chat_id(chat_id, *args, **kwargs):
    chat_group = get_repo_id_by_chat_group(chat_id)

    repo = get_repo_name_by_repo_id(chat_group.repo_id)
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
def open_repo_url(chat_id):
    try:
        url = get_repo_url_by_chat_id(chat_id)
        webbrowser.open(url)
        return True
    except Exception as e:
        logging.error(e)
    return False


@celery.task()
def open_repo_insight(chat_id):
    try:
        url = get_repo_url_by_chat_id(chat_id)
        webbrowser.open(f"{url}/pulse")
        return True
    except Exception as e:
        logging.error(e)
    return False


@celery.task()
def get_repo_url_by_chat_id(chat_id, *args, **kwargs):
    chat_group = get_repo_id_by_chat_group(chat_id)

    repo = get_repo_name_by_repo_id(chat_group.repo_id)
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
def open_repo_url(chat_id):
    try:
        url = get_repo_url_by_chat_id(chat_id)
        webbrowser.open(url)
        return True
    except Exception as e:
        logging.error(e)
    return False


@celery.task()
def open_repo_insight(chat_id):
    try:
        url = get_repo_url_by_chat_id(chat_id)
        webbrowser.open(f"{url}/pulse")
        return True
    except Exception as e:
        logging.error(e)
    return False


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
@with_lark_storage("repo_manual")
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


@celery.task()
@with_lark_storage("change_repo_visit")
def change_repo_visit(visibility, app_id, message_id, repo_id, *args, **kwargs):
    """修改 Repo 访问权限"""
    bot, application = get_bot_by_application_id(app_id)
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )

    if repo:
        # TODO 修改 repo 访问权限, 调用github api，修改数据库和调用api要用事务，db更新在github事件触发之后，天一处理
        # repo.visibility = True if visibility == "public" else False
        # db.session.commit()

        message = RepoTipSuccess(f"已成功修改 {repo.name} 仓库为 {visibility}")
        return bot.reply(message_id, message).json()

    return bot.reply(message_id, message).json()


@celery.task()
@with_lark_storage("change_repo_name")
def change_repo_name(name, app_id, message_id, repo_id, param, *args, **kwargs):
    """修改 Repo 标题"""
    bot, application = get_bot_by_application_id(app_id)
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )

    if repo:
        # TODO 修改 repo 标题, 调用github api，修改数据库和调用api要用事务
        repo.name = name
        db.session.commit()

        message = RepoTipSuccess(f"已成功修改 {repo.name} 仓库标题为 {name}")
        return bot.reply(message_id, message).json()

    return bot.reply(message_id, message).json()


@celery.task()
@with_lark_storage("change_repo_desc")
def change_repo_desc(desc, app_id, message_id, repo_id, param, *args, **kwargs):
    """编辑 Repo"""
    bot, application = get_bot_by_application_id(app_id)
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )

    if repo:
        # TODO 修改 repo 描述, 调用github api，修改数据库和调用api要用事务
        repo.description = desc
        db.session.commit()

        message = RepoTipSuccess(f"已成功修改 {repo.description} 仓库描述为 {desc}")
        return bot.reply(message_id, message).json()

    return bot.reply(message_id, message).json()


@celery.task()
@with_lark_storage("change_repo_link")
def change_repo_link(homepage, app_id, message_id, repo_id, param, *args, **kwargs):
    """关联 Repo"""
    bot, application = get_bot_by_application_id(app_id)
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )

    if repo:
        # TODO 修改 repo 描述, 调用github api，修改数据库和调用api要用事务
        repo.extra["homepage"] = homepage
        db.session.commit()

        message = RepoTipSuccess(f"已成功修改 {repo.description} 仓库主页为 {homepage}")
        return bot.reply(message_id, message).json()

    return bot.reply(message_id, message).json()


@celery.task()
@with_lark_storage("change_repo_label")
def label_repo(label, app_id, message_id, repo_id, param, *args, **kwargs):
    """标记 Repo"""
    bot, application = get_bot_by_application_id(app_id)
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )

    # TODO label 应该要有新增修改删除
    # if repo:
    #     # TODO 修改 repo 描述, 调用github api，修改数据库和调用api要用事务
    #     repo.extra["homepage"] = label
    #     db.session.commit()

    #     message = RepoTipSuccess(f"已成功修改 {repo.description} 仓库主页为 {homepage}")
    #     return bot.reply(message_id, message).json()

    return bot.reply(message_id, message).json()
