from app import app, db
from celery_app import celery
from model.schema import CodeApplication, Issue, ObjID, Repo, Team
from tasks.lark.pull_request import send_pull_request_card
from utils.github.model import PullRequestEvent
from utils.github.repo import GitHubAppRepo


@celery.task()
def on_pull_request(data: dict) -> list:
    """Parse and handle PullRequest event.

    Args:
        data (dict): Payload from GitHub webhook.

    Returns:
        str: Celery task ID.
    """
    try:
        event = PullRequestEvent(**data)
    except Exception as e:
        app.logger.error(f"Failed to parse PullRequest event: {e}")
        raise e

    action = event.action
    match action:
        case "opened":
            task = on_pull_request_opened.delay(event.model_dump())
            return [task.id]
        case _:
            app.logger.info(f"Unhandled PullRequest event action: {action}")
            return []


@celery.task()
def on_pull_request_opened(event_dict: dict | list | None) -> list:
    """Handle PullRequest opened event.

    Send PullRequest card message to Repo Owner.
    """
    try:
        event = PullRequest(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse PullRequest event: {e}")
        return []

    github_app = GitHubAppRepo(str(event.installation.id))

    pr_info = event.pull_request

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
    # 创建 pullrequest
    new_pr = Issue(
        id=ObjID.new_id(),
        repo_id=repo.id,
        pull_request_number=pr_info.number,
        title=pr_info.title,
        description=pr_info.body,
        extra=pr_info.model_dump(),
    )
    db.session.add(new_pr)
    db.session.commit()

    task = send_pull_request_card.delay(new_pr.id)

    return [task.id]
