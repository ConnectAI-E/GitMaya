from app import app, db
from celery_app import celery
from model.repo import create_repo_from_github
from model.schema import (
    BindUser,
    CodeApplication,
    IMApplication,
    Repo,
    RepoUser,
    Team,
    TeamMember,
)
from tasks.lark import update_repo_info
from tasks.lark.manage import send_detect_repo
from utils.github.model import ForkEvent, RepoEvent, StarEvent
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
            task = on_repository_updated.delay(event.model_dump())
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
            Team.status == 0,
        )
        .first()
    )
    if team is None:
        app.logger.error(f"Team {code_application.team_id} not found")
        return []

    # 创建 repo，同时创建配套的 repo_user
    new_repo = create_repo_from_github(
        repo=repo_info,
        org_name=team.name,
        application_id=code_application.id,
        github_app=github_app,
    )

    # 查找 RepoUser 中具有 admin 权限的用户
    admin_github_bind_users = (
        db.session.query(BindUser)
        .join(
            RepoUser,
            RepoUser.bind_user_id == BindUser.id,
        )
        .filter(
            RepoUser.repo_id == new_repo.id,
            RepoUser.permission == "admin",
            BindUser.platform == "github",
        )
        .all()
    )

    if len(admin_github_bind_users) == 0:
        app.logger.error(f"Repo {new_repo.id} has no github admin user")
        return []

    # 从 github_bind_users 中筛选出 lark_bind_users
    admin_lark_bind_users = (
        db.session.query(BindUser)
        .join(
            TeamMember,
            TeamMember.im_user_id == BindUser.id,
        )
        .filter(
            TeamMember.team_id == team.id,
            TeamMember.code_user_id.in_([user.id for user in admin_github_bind_users]),
            TeamMember.status == 0,
            BindUser.status == 0,
        )
        .all()
    )

    if len(admin_lark_bind_users) == 0:
        app.logger.error(f"Repo {new_repo.id} has no lark admin user")
        return []

    # 查找 im application
    im_application = (
        db.session.query(IMApplication)
        .filter(
            IMApplication.team_id == team.id,
        )
        .first()
    )

    task_ids = []
    for bind_user in admin_lark_bind_users:
        task = send_detect_repo.delay(
            repo_id=new_repo.id,
            app_id=im_application.app_id,
            open_id=bind_user.openid,
            topics=repo_info.get("topics", []),
            visibility="Private" if repo_info.get("private") else "Public",
        )

        task_ids.append(task.id)

    return task_ids


@celery.task()
def on_star(data: dict) -> list:
    """Handler for repository starred event.

    Args:
        data (dict): Payload from GitHub webhook.

    Returns:
        str: Celery task ID.
    """
    try:
        event = StarEvent(**data)
    except Exception as e:
        app.logger.error(f"Failed to parse star event: {e}")
        raise e

    task = on_repository_updated.delay(event.model_dump())

    return [task.id]


@celery.task()
def on_fork(data: dict) -> list:
    """Handler for repository starred event.

    Args:
        data (dict): Payload from GitHub webhook.

    Returns:
        str: Celery task ID.
    """
    try:
        event = ForkEvent(**data)
    except Exception as e:
        app.logger.error(f"Failed to parse fork event: {e}")
        raise e

    # fork 事件没有action属性，先暂时添加一个
    # TODO unfork 事件实际是 delete repo事件，比较复杂，需求比较边缘，目前还没实现，暂且放着
    event.action = "fork"
    task = on_repository_updated.delay(event.model_dump())

    return [task.id]


@celery.task()
def on_repository_updated(event_dict: dict | None) -> list[str]:
    """Handler for repository update.

    Update info for repo ino card.

    Args:
        event_dict (dict): Payload from GitHub webhook.

    Returns:
        list[str]: Celery task IDs.
    """

    try:
        event = RepoEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse repository event: {e}")
        return []

    # 更新数据库
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.repo_id == event.repository.id,
        )
        .first()
    )

    if repo is None:
        app.logger.error(f"Repo {event.repository.id} not found")
        return []

    repo.name = event.repository.name
    repo.description = event.repository.description
    repo.extra = event.repository.model_dump()

    db.session.commit()

    task = update_repo_info.delay(repo.id)

    return [task.id]
