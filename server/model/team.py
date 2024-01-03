from flask import abort
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
            CodeApplication.status == 0,
        )
        .first(),
        db.session.query(IMApplication)
        .filter(
            IMApplication.team_id == team_id,
            IMApplication.status == 0,
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
            IMApplication.status == 0,
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
