from flask import abort, session
from sqlalchemy import and_, or_
from utils.utils import query_one_page

from .schema import *


def get_team_list_by_user_id(user_id, page=1, size=100):
    query = db.session.query(Team).filter(
        or_(
            Team.user_id == user_id,  # 管理员
            and_(
                TeamMember.team_id == Team.id,
                TeamMember.code_user_id == user_id,  # 属于某个team的员工
                TeamMember.status == 0,
            ),
        ),
        Team.status == 0,
    )
    total = query.count()
    if total == 0:
        return [], 0
    return query_one_page(query, page, size), total


def is_team_admin(team_id, user_id):
    return (
        True
        if db.session.query(Team.id)
        .filter(
            Team.user_id == user_id,
            Team.status == 0,
        )
        .limit(1)
        .scalar()
        else False
    )


def get_team_by_id(team_id, user_id):
    team = (
        db.session.query(Team)
        .filter(
            or_(
                Team.user_id == user_id,  # 管理员
                and_(
                    TeamMember.team_id == Team.id,
                    TeamMember.code_user_id == user_id,  # 属于某个team的员工
                    TeamMember.status == 0,
                ),
            ),
            Team.status == 0,
        )
        .first()
    )
    if not team:
        return abort(404, "can not found team by id")
    return team


def get_application_info_by_team_id(team_id):
    # TODO
    return (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.team_id == team_id,
            CodeApplication.status.in_([0, 1]),
        )
        .first(),
        db.session.query(IMApplication)
        .filter(
            IMApplication.team_id == team_id,
            IMApplication.status.in_([0, 1]),
        )
        .first(),
    )


def get_team_member(team_id, user_id, page=1, size=20):
    query = db.session.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.status == 0,
    )
    # admin can get all users in current_team
    if not is_team_admin(team_id, user_id):
        query = query.filter(
            TeamMember.code_user_id == user_id,
        )
    total = query.count()
    if total == 0:
        return [], 0
    return query_one_page(query, page, size), total


def get_im_user_by_team_id(team_id, page=1, size=20):
    query = (
        db.session.query(BindUser)
        .join(
            IMApplication,
            IMApplication.id == BindUser.application_id,
        )
        .filter(
            IMApplication.team_id == team_id,
            IMApplication.status.in_([0, 1]),
            BindUser.status == 0,
        )
    )
    total = query.count()
    if total == 0:
        return [], 0
    return query_one_page(query, page, size), total

    data, total = get_im_user_by_team_id(team_id, page, size)


def set_team_member(team_id, code_user_id, im_user_id):
    db.session.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.code_user_id == code_user_id,
        TeamMember.status == 0,
    ).update(dict(im_user_id=im_user_id))
    db.session.commit()


def create_team(app_info: dict) -> Team:
    """Create a team.

    Args:
        name (str): Team name.
        app_info (dict): GitHub App info.

    Returns:
        Team: Team object.
    """

    current_user_id = session.get("user_id", None)
    if not current_user_id:
        abort(403, "can not found user by id")

    new_team = Team(
        id=ObjID.new_id(),
        user_id=current_user_id,
        name=app_info["account"]["login"],
        description=None,
        # extra=app_info,
    )

    db.session.add(new_team)
    db.session.flush()

    # 创建 TeamMember
    current_bind_user = BindUser.query.filter(
        BindUser.user_id == current_user_id,
        BindUser.status == 0,
    ).first()
    if not current_bind_user:
        abort(403, "can not found bind user by id")

    new_team_member = TeamMember(
        id=ObjID.new_id(),
        team_id=new_team.id,
        code_user_id=current_bind_user.id,
        im_user_id=None,
    )

    db.session.add(new_team_member)
    db.session.commit()

    return new_team


def create_code_application(team_id: str, installation_id: str) -> CodeApplication:
    """Create a code application.

    Args:
        team_id (str): Team ID.
        installation_id (str): GitHub App installation ID.

    Returns:
        CodeApplication: CodeApplication object.
    """

    new_code_application = CodeApplication(
        id=ObjID.new_id(),
        team_id=team_id,
        installation_id=installation_id,
    )

    db.session.add(new_code_application)
    db.session.commit()

    return new_code_application


def save_im_application(
    team_id, platform, app_id, app_secret, encrypt_key, verification_token
):
    application = (
        db.session.query(IMApplication).filter(IMApplication.app_id == app_id).first()
    )
    if not application:
        application = IMApplication(
            id=ObjID.new_id(),
            platform=platform,
            team_id=team_id,
            app_id=app_id,
            app_secret=app_secret,
            extra=dict(encrypt_key=encrypt_key, verification_token=verification_token),
        )
        db.session.add(application)
        db.session.commit()
    else:
        db.session.query(IMApplication).filter(
            IMApplication.id == application.id,
        ).update(
            dict(
                platform=platform,
                team_id=team_id,
                app_id=app_id,
                app_secret=app_secret,
                extra=dict(
                    encrypt_key=encrypt_key, verification_token=verification_token
                ),
            )
        )
        db.session.commit()