from app import app, db
from celery_app import celery
from model.schema import ObjID, PullRequest, Repo
from tasks.lark.pull_request import send_pull_request_card, update_pull_request_card
from utils.github.model import PullRequestEvent


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
            task = on_pull_request_updated.delay(event.model_dump())
            app.logger.info(f"Unhandled PullRequest event action: {action}")
            return []


@celery.task()
def on_pull_request_opened(event_dict: dict | list | None) -> list:
    """Handle PullRequest opened event.

    Send PullRequest card message to Repo Owner.
    """
    try:
        event = PullRequestEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse PullRequest event: {e}")
        return []

    pr_info = event.pull_request

    repo = db.session.query(Repo).filter(Repo.repo_id == event.repository.id).first()
    # 检查是否已经创建过 pullrequest
    pr = (
        db.session.query(PullRequest)
        .filter(
            PullRequest.repo_id == repo.id,
            PullRequest.pull_request_number == pr_info.number,
        )
        .first()
    )
    if pr:
        app.logger.info(f"PullRequest already exists: {pr.id}")
        return []

    # 创建 pullrequest
    new_pr = PullRequest(
        id=ObjID.new_id(),
        repo_id=repo.id,
        pull_request_number=pr_info.number,
        title=pr_info.title,
        description=pr_info.body,
        base=pr_info.base.ref,
        head=pr_info.head.ref,
        state=pr_info.state,
        extra=pr_info.model_dump(),
    )
    db.session.add(new_pr)
    db.session.commit()

    task = send_pull_request_card.delay(new_pr.id)

    return [task.id]


@celery.task()
def on_pull_request_updated(event_dict: dict) -> list:
    """Handle PullRequest updated event.

    Send PullRequest card message to Repo Owner.
    """
    try:
        event = PullRequestEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse PullRequest event: {e}")
        return []

    repo = db.session.query(Repo).filter(Repo.repo_id == event.repository.id).first()
    if repo is None:
        app.logger.error(f"Failed to find Repo: {event.repository.id}")
        return []

    pr = (
        db.session.query(PullRequest)
        .filter(PullRequest.repo_id == repo.id)
        .filter(PullRequest.pull_request_number == event.pull_request.number)
        .first()
    )
    if pr:
        pr.title = event.pull_request.title
        pr.description = event.pull_request.body
        pr.base = event.pull_request.base.ref
        pr.head = event.pull_request.head.ref
        pr.state = event.pull_request.state
        pr.extra = event.pull_request.model_dump()
        db.session.commit()

        task = update_pull_request_card.delay(pr.id)

        return [task.id]
    else:
        app.logger.error(f"Failed to find PullRequest: {event.pull_request.number}")
        return []
