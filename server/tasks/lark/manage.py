from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import CodeApplication, IMApplication, Repo, Team, db
from utils.lark.manage_manual import ManageManual
from utils.lark.manage_repo_detect import ManageRepoDetect


def get_bot_by_application_id(app_id):
    application = (
        db.session.query(IMApplication)
        .filter(
            IMApplication.app_id == app_id,
        )
        .first()
    )
    if application:
        return (
            Bot(
                app_id=application.app_id,
                app_secret=application.app_secret,
            ),
            application,
        )
    return None, None


@celery.task()
def send_manage_manual(app_id, message_id, *args, **kwargs):
    bot, application = get_bot_by_application_id(app_id)
    if application:
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


@celery.task()
def send_detect_repo(repo_id, app_id, open_id=""):
    """send new repo card message to user.

    Args:
        repo_id: repo.id.
        app_id: IMApplication.app_id.
        open_id: BindUser.open_id.
    """
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )
    if repo:
        bot, _ = get_bot_by_application_id(app_id)
        message = ManageRepoDetect(
            # TODO 这里需要使用team.name + repo_name拼接url
            repo_url="https://github.com/ConnectAI-E/GitMaya",
            repo_name=repo.name,
            repo_description=repo.description,
            repo_topic=repo.extra.get("topic", []),
            visibility=repo.extra.get("visibility", "私有仓库"),
        )
        return bot.send(
            open_id,
            message,
            receive_id_type="open_id",
        ).json()
    return False
