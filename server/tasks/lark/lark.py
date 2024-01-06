import logging

from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import (
    BindUser,
    ChatGroup,
    CodeApplication,
    IMApplication,
    ObjID,
    Repo,
    Team,
    User,
    db,
)
from sqlalchemy import func, or_
from utils.lark.manage_manual import ManageManual


@celery.task()
def test_task():
    logging.error("test_task")
    return 1


def get_contact_by_bot_and_department(bot, department_id):
    page_token, page_size = "", 50
    while True:
        url = f"{bot.host}/open-apis/contact/v3/users/find_by_department?page_token={page_token}&page_size={page_size}&department_id={department_id}"
        result = bot.get(url).json()
        for department_user_info in result.get("data", {}).get("items", []):
            yield department_user_info
        has_more = result.get("data", {}).get("has_more")
        if not has_more:
            break
        page_token = result.get("data", {}).get("page_token", "")


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

        for department_id in result.get("data", {}).get("department_ids", []):
            for department_user_info in get_contact_by_bot_and_department(
                bot, department_id
            ):
                yield department_user_info

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
            ).update(dict(status=1))
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
            "success to get_contact_fo_lark_application %r %r",
            application.id,
            len(user_ids),
        )


@celery.task()
def create_chat_group_for_repo(repo_id):
    """
    1. 按repo_id找到repo
    2. 尝试找对应的chat_group，如果已经存在了，就不创建
    3. 否则创建chat_group，然后保存chat_group
    """
    repo = db.session.query(Repo).filter(Repo.id == repo_id).first()
    if repo:
        chat_group = (
            db.session.query(ChatGroup)
            .filter(
                ChatGroup.repo_id == repo.id,
                ChatGroup.status == 0,
            )
            .first()
        )
        if chat_group:
            app.logger.info("chat_group exists. %r", chat_group.chat_id)
            return chat_group.id
        else:
            application = (
                db.session.query(IMApplication)
                .join(
                    Team,
                    Team.id == IMApplication.team_id,
                )
                .join(
                    CodeApplication,
                    CodeApplication.team_id == Team.id,
                )
                .filter(
                    Team.status == 0,
                    CodeApplication.status.in_([0, 1]),
                    IMApplication.status.in_([0, 1]),
                )
                .first()
            )
            if application:
                bot = Bot(
                    app_id=application.app_id,
                    app_secret=application.app_secret,
                )
                chat_group_url = f"{bot.host}/open-apis/im/v1/chats?uuid={repo.id}"
                name = f"{repo.name} 项目群"
                description = f"{repo.description}"
                result = bot.post(
                    chat_group_url,
                    json={
                        "name": name,
                        "description": description,
                        "edit_permission": "all_members",
                    },
                ).json()
                chat_id = result.get("data", {}).get("chat_id")
                if chat_id:
                    chat_group_id = ObjID.new_id()
                    chat_group = ChatGroup(
                        id=chat_group_id,
                        repo_id=repo.id,
                        im_application_id=application.id,
                        chat_id=chat_id,
                        name=name,
                        description=description,
                        extra=result,
                    )
                    db.session.add(chat_group)
                    db.session.commit()
                    return chat_group_id
    return


@celery.task()
def create_chat_group_for_all_repo():
    """
    1. 找出repo对应的群数量为空的repo_id
    """
    chat_group_count_column = func.count(ChatGroup.id)
    for repo_id, _ in (
        db.session.query(
            Repo.id,
            chat_group_count_column,
        )
        .join(
            ChatGroup,
            ChatGroup.repo_id == Repo.id,
        )
        .filter(
            Repo.status == 0,
            ChatGroup.status == 0,
        )
        .having(
            chat_group_count_column == 0,
        )
    ):
        result = create_chat_group_for_repo(repo_id)
        app.logger.info(
            "success to create_chat_group_for_repo %r %r",
            repo_id,
            result,
        )


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
