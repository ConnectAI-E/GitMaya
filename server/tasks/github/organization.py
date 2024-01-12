from app import app, db
from celery_app import celery
from model.schema import CodeApplication, Team
from utils.github.model import OrganizationEvent
from utils.user import add_team_member, create_github_member


@celery.task
def on_organization(event_dict: dict | None):
    try:
        event = OrganizationEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse Organization event: {e}")
        return []

    action = event.action
    match action:
        case "member_added":
            task = on_organization_member_added.delay(event.model_dump())
            return [task.id]
            # case "member_removed":
            #     task = on_organization_member_removed.delay(event.model_dump())
            #     return [task.id]
        case _:
            app.logger.info(f"Unhandled Organization event action: {action}")
            return []


@celery.task()
def on_organization_member_added(event_dict: dict) -> list:
    """Handle Organization member added event.

    Send Organization member added message to Repo Owner.

    Args:
        event_dict (dict): The dict of the event.

    Returns:
        list: user_id and bind_user_id.
    """
    try:
        event = OrganizationEvent(**event_dict)
    except Exception as e:
        app.logger.error(f"Failed to parse Organization event: {e}")
        return []

    user_info = event.membership.user

    # 根据 installation id 查询
    installation_id = event.installation.id
    code_application = (
        db.session.query(CodeApplication)
        .filter_by(installation_id=installation_id)
        .first()
    )

    if code_application is None:
        app.logger.error(f"Failed to get code application: {installation_id}")
        return []

    tema = db.session.query(Team).filter_by(id=code_application.team_id).first()
    if tema is None:
        app.logger.error(f"Failed to get team: {code_application.team_id}")
        return []

    user_id, bind_user_id = create_github_member(
        github_id=str(user_info.id),
        name=user_info.login,
        email=user_info.email,
        avatar=user_info.avatar_url,
        access_token=None,
        application_id=code_application.id,
        extra=user_info.model_dump(),
    )

    add_team_member(team_id=tema.id, code_user_id=bind_user_id)

    return [user_id, bind_user_id]
