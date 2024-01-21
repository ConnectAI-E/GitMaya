from app import app, db
from celery_app import celery
from model.schema import ChatGroup, PullRequest, Repo
from tasks.lark.base import get_bot_by_application_id
from utils.github.model import PushEvent
from utils.lark.pr_tip_commit_history import PrTipCommitHistory


@celery.task()
def on_push(data: dict | None) -> list:
    try:
        event = PushEvent(**data)
    except Exception as e:
        app.logger.error(f"Failed to parse PullRequest event: {e}")
        raise e

    # 查找有没有对应的 repo
    repo = db.session.query(Repo).filter(Repo.repo_id == event.repository.id).first()
    if not repo:
        app.logger.info(f"Repo not found: {event.repository.name}")
        return []

    pr = (
        db.session.query(PullRequest)
        .filter(
            PullRequest.repo_id == repo.id,
            PullRequest.head == "/".join((event.ref).split("/")[2:]),
            PullRequest.state == "open",
        )
        .first()
    )

    if pr is None:
        app.logger.info(f"PullRequest not found: {repo.name} {event.ref}")
        return []

    # 发送 Commit Log 信息
    chat_group = (
        db.session.query(ChatGroup).filter(ChatGroup.repo_id == repo.id).first()
    )
    if not chat_group:
        app.logger.info(f"ChatGroup not found: {repo.name}")
        return []

    bot, application = get_bot_by_application_id(chat_group.im_application_id)
    reply_result = bot.reply(
        pr.message_id,
        PrTipCommitHistory(
            commits=event.commits,
        ),
    )
    app.logger.info(f"Reply result: {reply_result}")
    return reply_result.json()
