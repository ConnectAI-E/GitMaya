from sqlalchemy import and_, or_

from .schema import User, db


def get_user_by_id(user_id):
    return (
        db.session.query(User)
        .filter(
            User.id == user_id,
            User.status == 0,
        )
        .first()
    )
