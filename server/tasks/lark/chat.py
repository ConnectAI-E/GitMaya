from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import ChatGroup, Repo, Team, db
from sqlalchemy.orm import aliased
from utils.lark.chat_manual import ChatManual
from utils.lark.chat_tip_failed import ChatTipFailed

from .manage import get_bot_by_application_id


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
        return send_manage_fail_message(
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
        return send_manage_fail_message(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    message = ManageManual(
        repo_url=f"https://github.com/{team.name}/{repo.name}",
        repo_name=repo.name,
        actions=[],  # TODO 获取actions
    )
    return bot.reply(message_id, message).json()
