from app import app, db
from celery_app import celery
from model.repo import create_repo_from_github
from model.schema import BindUser, CodeApplication, IMApplication, RepoUser, Team
from tasks.lark.manage import send_detect_repo
from utils.github.model import RepoEvent
from utils.github.repo import GitHubAppRepo


@celery.task()
def on_repository(data: dict) -> list:
    """Parse and handle repository event.

    Args:
        data (dict): Payload from GitHub webhook.

    Returns:
        str: Celery task ID.
    """
    try:
        event = RepoEvent(**data)
    except Exception as e:
        app.logger.error(f"Failed to parse repository event: {e}")
        raise e

    action = event.action
    match action:
        case "created":
            task = on_repository_created.delay(event.model_dump())
            return [task.id]
        case _:
            app.logger.info(f"Unhandled repository event action: {action}")
            return []


@celery.task()
def on_repository_created(event_dict: dict | list | None) -> list:
    """Handle repository created event.

    Send message to Repo Owner and create chat group for repo.
    """
    try:
        event = RepoEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse repository event: {e}")
        return []

    github_app = GitHubAppRepo(str(event.installation.id))

    # repo_info = github_app.get_repo_info(event.repository.id)
    repo_info = event.repository.model_dump()

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

    # 创建 repo，同时创建配套的 repo_user
    new_repo = create_repo_from_github(
        repo=repo_info,
        org_name=team.name,
        application_id=code_application.id,
        github_app=github_app,
    )

    # 查找 RepoUser 中具有 admin 权限的用户
    admin_bind_users = (
        db.session.query(BindUser)
        .join(
            RepoUser,
            RepoUser.bind_user_id == BindUser.id,
        )
        .filter(
            RepoUser.repo_id == new_repo.id,
            RepoUser.permission == "admin",
            BindUser.platform == "lark",
        )
        .all()
    )
    if len(admin_bind_users) == 0:
        app.logger.error(f"Repo {new_repo.id} has no admin user")
        return []

    # 查找 im application
    im_application = (
        db.session.query(IMApplication)
        .join(
            Team,
            IMApplication.team_id == Team.id,
        )
        .filter(
            IMApplication.status == 0,
        )
        .first()
    )

    task_ids = []
    for bind_user in admin_bind_users:
        task = send_detect_repo.delay(
            repo_id=new_repo.id,
            app_id=im_application.app_id,
            open_id=bind_user.openid,
            topics=repo_info.get("topics", []),
            visibility="Private" if repo_info.get("private") else "Public",
        )

        task_ids.append(task)

    return task_ids
