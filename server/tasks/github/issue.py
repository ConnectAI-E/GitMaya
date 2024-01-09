from app import app, db
from celery_app import celery
from model.schema import CodeApplication, Issue, ObjID, Repo, Team
from tasks.lark.issue import send_issue_card
from utils.github.model import IssueEvent
from utils.github.repo import GitHubAppRepo


@celery.task()
def on_issue_comment(data: dict) -> list:
    # TODO
    pass


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
        case _:
            app.logger.info(f"Unhandled issue event action: {action}")
            return []


@celery.task()
def on_issue_opened(event_dict: dict | list | None) -> list:
    """Handle issue opened event.

    Send issue card message to Repo Owner.
    """
    try:
        event = IssueEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse issue event: {e}")
        return []

    github_app = GitHubAppRepo(str(event.installation.id))

    issue_info = event.issue

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.installation_id == str(event.installation.id),
            CodeApplication.status == 0,
        )
        .first()
    )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == code_application.team_id,
        )
        .first()
    )

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

    task = send_issue_card.delay(new_issue.id)

    return [task.id]
