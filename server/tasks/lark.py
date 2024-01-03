import logging

from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import BindUser, IMApplication, ObjID, User, db
from sqlalchemy import or_


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
    """
    1. 按application_id找到application
    2. 获取所有能用当前应用的人员
    3. 尝试创建bind_user + user
    4. 标记已经拉取过应用人员
    """
    user_ids = []
    application = (
        db.session.query(IMApplication)
        .filter(
            or_(
                IMApplication.id == application_id,
                IMApplication.app_id == application_id,
            ),
            IMApplication.status.in_([0, 1]),
        )
        .first()
    )
    if application:
        bot = Bot(
            app_id=application.app_id,
            app_secret=application.app_secret,
        )
        try:
            for item in get_contact_by_bot(bot):
                # add bind_user and user
                bind_user_id = (
                    db.session.query(BindUser.id)
                    .filter(
                        BindUser.openid == item["open_id"],
                        BindUser.status == 0,
                    )
                    .limit(1)
                    .scalar()
                )
                if not bind_user_id:
                    user_id = (
                        db.session.query(User.id)
                        .filter(
                            User.unionid == item["union_id"],
                            User.status == 0,
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
                        db.session.add(user)
                        db.session.flush()
                    bind_user_id = ObjID.new_id()
                    bind_user = BindUser(
                        id=bind_user_id,
                        user_id=user_id,
                        platform="lark",
                        application_id=application_id,
                        unionid=item["union_id"],
                        openid=item["open_id"],
                        name=item["name"],
                        avatar=item["avatar"]["avatar_origin"],
                        extra=item,
                    )
                    db.session.add(bind_user)
                    db.session.commit()
                    user_ids.append(bind_user_id)
            db.session.query(IMApplication).filter(
                IMApplication.id == application.id,
            ).update(dist(status=1))
            db.session.commit()
        except Exception as e:
            # can not get contacts
            app.logger.exception(e)

    return user_ids


@celery.task()
def get_contact_for_all_lark_application():
    for application in db.session.query(IMApplication).filter(
        IMApplication.status == 0,
    ):
        user_ids = get_contact_by_lark_application(application.id)
        app.logger.info(
            "success to get_contact_fo_lark_application %r %r", app.id, len(user_ids)
        )
