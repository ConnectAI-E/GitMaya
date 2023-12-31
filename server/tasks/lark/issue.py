import json
import logging

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
from utils.github.repo import GitHubAppRepo
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
            bot, application = get_bot_by_application_id(chat_group.im_application_id)
            team = db.session.query(Team).filter(Team.id == application.team_id).first()
            if application and team:
                repo_url = f"https://github.com/{team.name}/{repo.name}"
                message = IssueCard(
                    repo_url=repo_url,
                    id=issue.issue_number,
                    title=issue.title,
                    description=issue.description,
                    status="待完成",
                    assignees=[],
                    tags=[],
                    updated=issue.modified.strftime("%Y-%m-%d %H:%M:%S"),
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
                        # 第一条话题消息，直接放repo_url
                        FeishuTextMessage(f'<at user_id="all">所有人</at>\n{repo_url}'),
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

                status = issue.extra.get("state", "opened")
                if status == "closed":
                    status = "已关闭"
                else:
                    status = "待完成"

                message = IssueCard(
                    repo_url=repo_url,
                    id=issue.issue_number,
                    title=issue.title,
                    description=issue.description,
                    status=status,
                    assignees=issue.extra.get("assignees", []),
                    tags=issue.extra.get("labels", []),
                    updated=issue.modified.strftime("%Y-%m-%d %H:%M:%S"),
                )

                result = bot.update(
                    message_id=issue.message_id,
                    content=message,
                )

                return result.json()

    return False


@celery.task()
def create_issue_comment(app_id, message_id, content, data, *args, **kwargs):
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

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.id == repo.application_id,
        )
        .first()
    )
    if not code_application:
        return send_issue_failed_tip(
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
        return send_issue_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, **kwargs
        )

    openid = data["event"]["sender"]["sender_id"]["open_id"]
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
    response = github_app.create_issue_comment(
        team.name, repo.name, issue.issue_number, content["text"]
    )
    if "id" not in response:
        return send_issue_failed_tip(
            "同步消息失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response
