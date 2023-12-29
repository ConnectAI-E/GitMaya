from .schema import IMApplication, db


def get_bot_by_app_id(app_id):
    return (
        db.session.query(IMApplication)
        .filter(
            IMApplication.app_id == app_id,
        )
        .first()
    )
