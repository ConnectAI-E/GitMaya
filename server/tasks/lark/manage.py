import logging
from math import log

from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import (
    BindUser,
    ChatGroup,
    CodeApplication,
    IMApplication,
    ObjID,
    Repo,
    RepoUser,
    Team,
    TeamMember,
    db,
)
from repo import send_repo_info
from sqlalchemy.orm import aliased
from utils.lark.manage_fail import ManageFaild
from utils.lark.manage_manual import ManageManual
from utils.lark.manage_repo_detect import ManageRepoDetect
from utils.lark.manage_success import ManageSuccess


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
        bot, application = get_bot_by_application_id(app_id)
        team = (
            db.session.query(Team)
            .filter(
                Team.id == application.team_id,
            )
            .first()
        )
        message = ManageRepoDetect(
            # TODO 这里需要使用team.name + repo_name拼接url
            repo_url=f"https://github.com/{team.name}/{repo.name}",
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


@celery.task()
def send_manage_fail_message(content, app_id, message_id, *args, bot=None, **kwargs):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: error message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = ManageFaild(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_manage_success_message(content, app_id, message_id, *args, bot=None, **kwargs):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: success message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = ManageSuccess(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def create_chat_group_for_repo(
    repo_url, chat_name, app_id, message_id, *args, **kwargs
):
    """
    user input:
    /match repo_url chat_name

    Args:
        repo_url: repo_url.
        chat_name: chat_name.
        app_id: IMApplication.app_id.
        message_id: lark message id.
    """
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_manage_fail_message(
            "找不到对应的应用", app_id, message_id, *args, bot=bot, **kwargs
        )
    team = (
        db.session.query(Team)
        .filter(
            Team.id == application.team_id,
        )
        .first()
    )
    if not team:
        return send_manage_fail_message(
            "找不到对应的项目", app_id, message_id, *args, bot=bot, **kwargs
        )

    # TODO
    repo_name = repo_url.split("/").pop()
    repo = (
        db.session.query(Repo)
        .join(
            CodeApplication,
            Repo.application_id == CodeApplication.id,
        )
        .filter(
            CodeApplication.team_id == team.id,
            Repo.name == repo_name,
        )
        .first()
    )
    if not repo:
        return send_manage_fail_message(
            "找不到对应的项目", app_id, message_id, *args, bot=bot, **kwargs
        )

    chat_group = (
        db.session.query(ChatGroup)
        .filter(
            ChatGroup.repo_id == repo.id,
            ChatGroup.status == 0,
        )
        .first()
    )
    if chat_group:
        return send_manage_fail_message(
            "不允许重复创建项目群", app_id, message_id, *args, bot=bot, **kwargs
        )

    # 持有相同uuid的请求10小时内只可成功创建1个群聊
    chat_group_url = f"{bot.host}/open-apis/im/v1/chats?uuid={repo.id}"
    # TODO 这里是一个可以配置的模板
    name = chat_name or f"{repo.name} 项目群"
    description = f"{repo.description}"
    # TODO 当前先使用发消息的人，后面查找这个项目的所有者...
    try:
        # parser.parse_args(text, bot.app_id, message_id, content, *args, **kwargs)
        owner_id = args[1]["event"]["sender"]["sender_id"]["open_id"]
    except Exception as e:
        logging.error(e)
        # card event
        owner_id = args[0]["open_id"]
    CodeUser = aliased(BindUser)
    IMUser = aliased(BindUser)
    # user_id_list 使用这个项目绑定的人的列表，同时属于当前repo
    user_id_list = [
        openid
        for openid, in db.session.query(IMUser.openid)
        .join(
            TeamMember,
            TeamMember.im_user_id == IMUser.id,
        )
        .join(CodeUser, TeamMember.code_user_id == CodeUser.id)
        .join(
            RepoUser,
            RepoUser.bind_user_id == CodeUser.id,
        )
        .filter(
            TeamMember.team_id == team.id,
            RepoUser.repo_id == repo.id,
        )
    ] + [owner_id]

    result = bot.post(
        chat_group_url,
        json={
            "name": name,
            "description": description,
            "edit_permission": "all_members",  # TODO all_members/only_owner
            "set_bot_manager": True,  # 设置创建群的机器人为管理员
            "owner_id": owner_id,
            "user_id_list": user_id_list,
        },
    ).json()
    chat_id = result.get("data", {}).get("chat_id")
    if not chat_id:
        content = f"创建项目群失败:\n\n{result.get('msg')}"
        return send_manage_fail_message(
            content, app_id, message_id, *args, bot=bot, **kwargs
        )

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
    content = "\n".join(
        [
            f"1. 成功创建名为「{name}」的新项目群",
            # TODO 这里需要给人发邀请???创建群的时候，可以直接拉群...
        ]
    )

    # 新建群后自动发 Repo info，并且pin
    try:
        send_repo_info_data = send_repo_info(
            repo.id,
            app_id,
            chat_group_id,
            *args,
            **kwargs,
        )
        logging.info("send_repo_info success")

        repo_info_message_id = send_repo_info_data["data"]["message_id"]

        bot.pin(bot, repo_info_message_id)
        logging.info("pin_repo_info success")

        # 创建群聊话题，并回复第一条内容(repo_url)

    except Exception as e:
        logging.error(e)

    return send_manage_success_message(
        content, app_id, message_id, *args, bot=bot, **kwargs
    )


# TODO 可能需要加到sdk中
def pin(bot, message_id):
    # https://open.feishu.cn/open-apis/im/v1/messages/:message_id
    url = f"{bot.host}/open-apis/im/v1/pins"
    body = {"message_id": message_id}
    return bot.post(url, json=body)
