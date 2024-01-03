import logging

from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import IMApplication, db


@celery.task()
def test_task():
    logging.error("test_task")
    return 1


def get_contact_by_bot(bot):
    page_token, page_size = "", 100
    while True:
        url = f"{bot.host}/open-apis/contact/v3/scopes?page_token={page_token}&page_size={page_size}"
        result = bot.get(url).json()
        for open_id in result.get("data", {}).get("user_ids", []):
            # https://open.feishu.cn/open-apis/contact/v3/users/:user_id
            user_info_url = (
                f"{bot.host}/open-apis/contact/v3/users/{open_id}?user_id_type=open_id"
            )
            user_info = bot.get(user_info_url).json()
            if user_info.get("data", {}).get("user"):
                yield user_info.get("data", {}).get("user")
            else:
                app.logger.error("can not get user_info %r", user_info)
        has_more = result.get("data", {}).get("has_more")
        if not has_more:
            break
        page_token = result.get("data", {}).get("page_token", "")


@celery.task()
def get_contact_by_lark_application(application_id):
    application = (
        db.session.query(IMApplication)
        .filter(
            IMApplication.id == application_id,
            IMApplication.status == 0,
        )
        .first()
    )
    if application:
        bot = Bpt(
            app_id=application.app_id,
            app_secret=application.app_secret,
        )
        for user in get_contact_by_bot(bot):
            app.logger.info("debug user %r", user)
