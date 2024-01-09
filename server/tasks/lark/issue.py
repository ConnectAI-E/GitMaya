import json
import logging

from celery_app import app, celery
from model.schema import ChatGroup, Issue, Repo, Team, db
from utils.lark.issue_card import IssueCard
from utils.lark.issue_manual_help import IssueManualHelp
from utils.lark.issue_tip_failed import IssueTipFailed
from utils.lark.issue_tip_success import IssueTipSuccess

from .base import get_bot_by_application_id, get_git_object_by_message_id


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


@celery.task()
def send_issue_manual(app_id, message_id, content, data, *args, **kwargs):
    root_id = data["event"]["message"]["root_id"]
    _, issue, _ = get_git_object_by_message_id(root_id)
    if not issue:
        return send_issue_failed_tip(
            "找不到Issue", app_id, message_id, content, data, *args, **kwargs
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

    message = IssueManualHelp(
        repo_url=f"https://github.com/{team.name}/{repo.name}",
        issue_id=issue.issue_number,
        # TODO 这里需要找到真实的值
        persons=[],
        assignees=[],
        tags=[],
    )
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
            bot, application = get_bot_by_application_id(chat_group.application_id)
            team = db.session.query(Team).filter(Team.id == application.team_id).first()
            if application and team:
                message = IssueCard(
                    repo_url=f"https://github.com/{team.name}/{repo.name}",
                    id=issue.issue_number,
                    title=issue.title,
                    description=issue.description,
                    status="待完成",
                    assignees=[],
                    tags=[],
                    updated=issue.modified.strftime("%Y-%m-%d %H:%M:%S"),
                )
                return bot.send(
                    chat_group.chat_id, message, receive_id_type="chat_id"
                ).json()
    return False
