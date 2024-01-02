from flask import abort
from sqlalchemy import and_, or_
from utils.utils import query_one_page

from .schema import Team, TeamMember, db


def get_team_list_by_user_id(user_id, page=1, size=100):
    query = db.session.query(Team).filter(
        or_(
            Team.user_id == user_id,  # 管理员
            and_(
                TeamMember.team_id == Team.id,
                TeamMember.code_user_id == user_id,  # 属于某个team的员工
                TeamMember.status == 0,
            ),
            Team.status == 0,
        )
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
                Team.status == 0,
            )
        )
        .first()
    )
    if not team:
        return abort(404, "can not found team by id")
    return team
