import json
import logging

from celery_app import app, celery
from model.schema import ChatGroup, PullRequest, Repo, Team, db
from utils.lark.pr_card import PullCard
from utils.lark.pr_manual import PrManual
from utils.lark.pr_tip_failed import PrTipFailed
from utils.lark.pr_tip_success import PrTipSuccess

from .base import get_bot_by_application_id, get_git_object_by_message_id


@celery.task()
def send_pull_request_failed_tip(
    content, app_id, message_id, *args, bot=None, **kwargs
):
    """send new card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: error message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = PrTipFailed(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_pull_request_success_tip(
    content, app_id, message_id, *args, bot=None, **kwargs
):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: success message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = PrTipSuccess(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_pull_request_manual(app_id, message_id, content, data, *args, **kwargs):
    root_id = data["event"]["message"]["root_id"]
    _, _, pr = get_git_object_by_message_id(root_id)
    if not pr:
        return send_pull_request_failed_tip(
            "找不到PullRequest", app_id, message_id, content, data, *args, **kwargs
        )
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == pr.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    if not repo:
        return send_pull_request_failed_tip(
            "找不到项目", app_id, message_id, content, data, *args, **kwargs
        )
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_pull_request_failed_tip(
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
        return send_pull_request_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    message = PrManual(
        repo_url=f"https://github.com/{team.name}/{repo.name}",
        pr_id=pr.pull_request_number,
        # TODO 这里需要找到真实的值
        persons=[],
        assignees=[],
        tags=[],
    )
    # 回复到话题内部
    return bot.reply(message_id, message).json()


@celery.task()
def send_pull_request_card(pull_request_id):
    """send new PullRequest card message to user.

    Args:
        pull_request_id: PullRequest.id.
    """
    pr = db.session.query(PullRequest).filter(PullRequest.id == pull_request_id).first()
    if pr:
        chat_group = (
            db.session.query(ChatGroup)
            .filter(
                ChatGroup.repo_id == pr.repo_id,
            )
            .first()
        )
        repo = db.session.query(Repo).filter(Repo.id == pr.repo_id).first()
        if chat_group and repo:
            bot, application = get_bot_by_application_id(chat_group.application_id)
            team = db.session.query(Team).filter(Team.id == application.team_id).first()
            if application and team:
                message = PullCard(
                    repo_url=f"https://github.com/{team.name}/{repo.name}",
                    id=pr.pull_request_id,
                    title=pr.title,
                    description=pr.description,
                    # TODO
                    status="待完成",
                    updated=pr.modified.strftime("%Y-%m-%d %H:%M:%S"),
                )
                result = bot.send(
                    chat_group.chat_id, message, receive_id_type="chat_id"
                ).json()
                message_id = result.get("data", {}).get("message_id")
                if message_id:
                    # save message_id
                    issue.message_id = message_id
                    db.session.commit()
                    first_message_result = bot.reply(
                        message_id,
                        # TODO 第一条话题消息，直接放repo_url
                        FeishuTextMessage(f'<at user_id="all">所有人</at>\n{repo_url}'),
                        reply_in_thread=True,
                    ).json()
                    logging.info("debug first_message_result %r", first_message_result)
                return result
    return False
