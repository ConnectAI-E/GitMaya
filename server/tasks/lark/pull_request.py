import json
import logging

from celery_app import app, celery
from connectai.lark.sdk import FeishuTextMessage
from model.schema import (
    ChatGroup,
    CodeApplication,
    CodeUser,
    IMUser,
    PullRequest,
    Repo,
    Team,
    TeamMember,
    db,
)
from utils.github.repo import GitHubAppRepo
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
            bot, application = get_bot_by_application_id(chat_group.im_application_id)
            team = db.session.query(Team).filter(Team.id == application.team_id).first()
            if application and team:
                repo_url = f"https://github.com/{team.name}/{repo.name}"
                message = PullCard(
                    repo_url=repo_url,
                    id=pr.pull_request_number,
                    title=pr.title,
                    description=pr.description,
                    base=pr.extra.get("base", {}),
                    head=pr.extra.get("head", {}),
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
                    pr.message_id = message_id
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


@celery.task()
def send_pull_request_comment(pull_request_id, comment, user_name: str):
    """send new pull_request comment message to user.

    Args:
        pull_request_id: PullRequest.id.
        comment: str
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
        if chat_group and pr.message_id:
            bot, _ = get_bot_by_application_id(chat_group.im_application_id)
            result = bot.reply(
                pr.message_id,
                FeishuTextMessage(f"@{user_name}: {comment}"),
            ).json()
            return result
    return False


@celery.task()
def update_pull_request_card(pr_id: str) -> bool | dict:
    """Update PullRequest card message.

    Args:
        pr_id (str): PullRequest.id.
    Returns:
        bool | dict: True or False or FeishuMessage
    """

    pr = db.session.query(PullRequest).filter(PullRequest.id == pr_id).first()
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
            bot, application = get_bot_by_application_id(chat_group.im_application_id)
            team = db.session.query(Team).filter(Team.id == application.team_id).first()
            if application and team:
                repo_url = f"https://{team.name}/{repo.name}"

                status = pr.extra.get("state", "待完成")

                message = PullCard(
                    repo_url=repo_url,
                    id=pr.pull_request_number,
                    title=pr.title,
                    description=pr.description,
                    base=pr.extra.get("base", {}),
                    head=pr.extra.get("head", {}),
                    status=status,
                    assignees=pr.extra.get("assignees", []),
                    labels=pr.extra.get("labels", []),
                    updated=pr.modified.strftime("%Y-%m-%d %H:%M:%S"),
                )
                result = bot.update(pr.message_id, message).json()
                return result

    return False


@celery.task()
def create_pull_request_comment(app_id, message_id, content, data, *args, **kwargs):
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

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.id == repo.application_id,
        )
        .first()
    )
    if not code_application:
        return send_pull_request_failed_tip(
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
        return send_pull_request_failed_tip(
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
        team.name, repo.name, pr.pull_request_number, content["text"]
    )
    if "id" not in response:
        return send_pull_request_failed_tip(
            "同步消息失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response
