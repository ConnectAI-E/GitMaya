from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import CodeApplication, IMApplication, Repo, Team, db
from utils.lark.manage_manual import ManageManual


@celery.task()
def send_manage_manual(app_id, message_id, *args, **kwargs):
    application = (
        db.session.query(IMApplication)
        .filter(
            IMApplication.app_id == app_id,
        )
        .first()
    )
    if application:
        bot = Bot(
            app_id=application.app_id,
            app_secret=application.app_secret,
        )
        team = (
            db.session.query(Team)
            .filter(
                Team.id == application.team_id,
                Team.status == 0,
            )
            .first()
        )
        if team:
            repos = (
                db.session.query(Repo)
                .join(
                    CodeApplication,
                    Repo.application_id == CodeApplication.id,
                )
                .join(Team, CodeApplication.team_id == team.id)
                .filter(
                    Team.id == team.id,
                    Repo.status == 0,
                )
                .order_by(
                    Repo.modified.desc(),
                )
                .limit(20)
                .all()
            )
            message = ManageManual(
                org_name=team.name,
                repos=[(repo.id, repo.name) for repo in repos],
                team_id=team.id,
            )
            return bot.reply(message_id, message).json()
    return False
