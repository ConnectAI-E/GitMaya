from sqlalchemy import and_, or_

from .schema import Team, TeamMember, db


def query_one_page(query, page, size):
    offset = (page - 1) * int(size)
    return (
        query.offset(offset if offset > 0 else 0).limit(size if size > 0 else 0).all()
    )


def get_team_list_by_user_id(app_id, page=1, size=20):
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
    return query_one_page(query, page, size), total
