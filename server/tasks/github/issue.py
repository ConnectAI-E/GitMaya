import os

from app import app, db
from celery_app import celery
from model.schema import (
    BindUser,
    CodeApplication,
    Issue,
    ObjID,
    PullRequest,
    Repo,
    Team,
    TeamMember,
    User,
)
from tasks.lark.issue import send_issue_card, send_issue_comment, update_issue_card
from tasks.lark.pull_request import send_pull_request_comment
from utils.github.model import IssueCommentEvent, IssueEvent


@celery.task()
def on_issue_comment(data: dict) -> list:
    """Parse and handle issue commit event.

    Args:
        data (dict): Payload from GitHub webhook.

    Returns:
        str: Celery task ID.
    """
    try:
        event = IssueCommentEvent(**data)
    except Exception as e:
        app.logger.error(f"Failed to parse issue event: {e}")
        raise e

    if (
        event.comment.performed_via_github_app
        and event.comment.performed_via_github_app.name
        == os.environ.get("GITHUB_APP_NAME")
    ):
        return []

    action = event.action
    match action:
        case "created":
            task = on_issue_comment_created.delay(event.model_dump())
            return [task.id]
        case _:
            app.logger.info(f"Unhandled issue event action: {action}")
            return []


@celery.task()
def on_issue_comment_created(event_dict: dict | list | None) -> list:
    """Handle issue comment created event.

    Send issue card message to Repo Owner.
    """
    try:
        event = IssueCommentEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse issue event: {e}")
        return []

    repo = db.session.query(Repo).filter(Repo.repo_id == event.repository.id).first()
    if repo:
        if hasattr(event.issue, "pull_request") and event.issue.pull_request:
            pr = (
                db.session.query(PullRequest)
                .filter(
                    PullRequest.repo_id == repo.id,
                    PullRequest.pull_request_number == event.issue.number,
                )
                .first()
            )
            if pr:
                task = send_pull_request_comment.delay(
                    pr.id, event.comment.body, event.sender.login
                )
                return [task.id]
        else:
            issue = (
                db.session.query(Issue)
                .filter(
                    Issue.repo_id == repo.id,
                    Issue.issue_number == event.issue.number,
                )
                .first()
            )
            if issue:
                task = send_issue_comment.delay(
                    issue.id, event.comment.body, event.sender.login
                )
                return [task.id]

    return []


@celery.task()
def on_issue(data: dict) -> list:
    """Parse and handle issue event.

    Args:
        data (dict): Payload from GitHub webhook.

    Returns:
        str: Celery task ID.
    """
    try:
        event = IssueEvent(**data)
    except Exception as e:
        app.logger.error(f"Failed to parse issue event: {e}")
        raise e

    action = event.action
    match action:
        case "opened":
            task = on_issue_opened.delay(event.model_dump())
            return [task.id]
        # TODO: 区分已关闭的 Issue
        case _:
            task = on_issue_updated.delay(event.model_dump())
            # app.logger.info(f"Unhandled issue event action: {action}")
            return [task.id]


@celery.task()
def on_issue_opened(event_dict: dict | None) -> list:
    """Handle issue opened event.

    Send issue card message to Repo Owner.

    Args:
        event_dict (dict | None): Payload from GitHub webhook.

    Returns:
        list: Celery task ID.
    """
    try:
        event = IssueEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse issue event: {e}")
        return []

    issue_info = event.issue

    repo = db.session.query(Repo).filter(Repo.repo_id == event.repository.id).first()
    # 创建 issue
    new_issue = Issue(
        id=ObjID.new_id(),
        repo_id=repo.id,
        issue_number=issue_info.number,
        title=issue_info.title,
        description=issue_info.body,
        extra=issue_info.model_dump(),
    )
    db.session.add(new_issue)
    db.session.commit()

    github_user_id = event.sender.id
    installation_id = event.installation.id
    user = db.session.query(User).filter(User.unionid == github_user_id).first()
    if not user:
        task = send_issue_card.delay(new_issue.id)
    else:
        code_application = (
            db.session.query(CodeApplication)
            .filter(CodeApplication.installation_id == installation_id)
            .first()
        )

        team = (
            db.session.query(Team)
            .filter(Team.id == code_application.team_id, Team.status.in_([1, 0]))
            .first()
        )

        team_member = (
            db.session.query(TeamMember)
            .join(BindUser, TeamMember.code_user_id == BindUser.id)
            .filter(
                TeamMember.team_id == team.id,
                BindUser.user_id == user.id,
                BindUser.platform == "github",
            )
            .first()
        )

        im_bind_user = (
            db.session.query(BindUser)
            .filter(
                BindUser.user_id == user.id,
                BindUser.id == team_member.im_user_id,
                BindUser.platform == "lark",
            )
            .first()
        )

        task = send_issue_card.delay(
            new_issue.id, im_bind_user.openid, im_bind_user.name
        )

    return [task.id]


@celery.task()
def on_issue_updated(event_dict: dict) -> list:
    try:
        event = IssueEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse issue event: {e}")
        return []

    issue_info = event.issue

    repo = db.session.query(Repo).filter(Repo.repo_id == event.repository.id).first()
    # 修改 issue
    issue = (
        db.session.query(Issue)
        .filter(Issue.repo_id == repo.id, Issue.issue_number == issue_info.number)
        .first()
    )

    if issue:
        issue.title = issue_info.title
        issue.description = issue_info.body
        issue.extra = issue_info.model_dump()

        db.session.commit()

    else:
        app.logger.error(f"Failed to find issue: {event_dict}")
        return []

    task = update_issue_card.delay(issue.id)

    return [task.id]
