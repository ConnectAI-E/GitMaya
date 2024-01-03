import logging

from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import BindUser, IMApplication, ObjID, User, db


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
    user_ids = []
    application = (
        db.session.query(IMApplication)
        .filter(
            IMApplication.id == application_id,
            IMApplication.status == 0,
        )
        .first()
    )
    if application:
        bot = Bot(
            app_id=application.app_id,
            app_secret=application.app_secret,
        )
        for item in get_contact_by_bot(bot):
            # add bind_user and user
            app.logger.info("debug user %r", item)
            user_id = (
                db.session.query(BindUser.id)
                .filter(
                    BindUser.unionid == item["union_id"],
                    BindUser.status == 0,
                )
                .limit(1)
                .scalar()
            )
            if not user_id:
                user_id = ObjID.new_id()
                user = User(
                    id=user_id,
                    unionid=item["union_id"],
                    name=item["name"],
                    avatar=item["avatar"]["avatar_origin"],
                )
                bind_user = BindUser(
                    id=user_id,
                    user_id=user_id,
                    platform="lark",
                    application_id=application_id,
                    unionid=item["union_id"],
                    openid=item["open_id"],
                    name=item["name"],
                    avatar=item["avatar"]["avatar_origin"],
                    extra=item,
                )
                db.session.add_all([user, bind_user])
                db.session.commit()
                user_ids.append(user_id)

    return user_ids
