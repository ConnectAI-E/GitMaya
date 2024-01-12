import logging
import webbrowser
from math import log

from celery_app import app, celery
from connectai.lark.sdk import Bot, FeishuShareChatMessage, FeishuTextMessage
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
from sqlalchemy.orm import aliased
from utils.lark.manage_fail import ManageFaild
from utils.lark.manage_manual import ManageManual
from utils.lark.manage_repo_detect import ManageRepoDetect
from utils.lark.manage_success import ManageSuccess
from utils.lark.repo_info import RepoInfo

from .base import get_bot_by_application_id


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
def send_detect_repo(
    repo_id, app_id, open_id="", topics: list = [], visibility: str = "private"
):
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
            repo_topic=topics,
            visibility=visibility,
        )
        return bot.send(
            open_id,
            message,
            receive_id_type="open_id",
        ).json()
    return False


@celery.task()
def send_manage_fail_message(
    content, app_id, message_id, data, raw_message, *args, bot=None, **kwargs
):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: error message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = ManageFaild(content=content)
    open_id = raw_message["event"]["sender"]["sender_id"].get("open_id", None)
    return bot.send(open_id, message).json()


@celery.task()
def send_manage_success_message(
    content, app_id, message_id, data, raw_message, *args, bot=None, **kwargs
):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: success message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    open_id = raw_message["event"]["sender"]["sender_id"].get("open_id", None)
    return bot.send(open_id, message).json()


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
        try:
            message = FeishuShareChatMessage(chat_id=chat_group.chat_id)
            open_id = raw_message["event"]["sender"]["sender_id"].get("open_id", None)
            bot.send(open_id, message).json()
        except Exception as e:
            logging.error(e)
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
    """
    创建项目群之后，需要发两条消息：
    1. 给操作的用户发成功的消息
    2. 给群发送repo 卡片消息，并pin
    """
    content = "\n".join(
        [
            f"1. 成功创建名为「{name}」的新项目群",
            # TODO 这里需要给人发邀请???创建群的时候，可以直接拉群...
        ]
    )
    # 这里可以再触发一个异步任务给群发卡片，不过为了保存结果，就同步调用
    result = send_repo_to_chat_group(repo.id, app_id, chat_id) + [
        send_manage_success_message(
            content, app_id, message_id, *args, bot=bot, **kwargs
        )
    ]
    return result


@celery.task()
def send_repo_to_chat_group(repo_id, app_id, chat_id=""):
    """send new repo card message to user.

    Args:
        repo_id: repo.id.
        app_id: IMApplication.app_id.
        chat_id: ChatGroup.chat_id.
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
        repo_url = f"https://github.com/{team.name}/{repo.name}"
        message = RepoInfo(
            repo_url=repo_url,
            repo_name=repo.name,
            repo_description=repo.description,
            repo_topic=repo.extra.get("topics", []),
            homepage=repo.extra.get("homepage", repo_url),
            open_issues_count=repo.extra.get("open_issues_count", 0),
            stargazers_count=repo.extra.get("stargazers_count", 0),
            forks_count=repo.extra.get("forks_count", 0),
            visibility="私有仓库" if repo.extra.get("private") else "公开仓库",
            updated=repo.extra.get("updated_at", ""),
        )
        result = bot.send(
            chat_id,
            message,
            receive_id_type="chat_id",
        ).json()
        message_id = result.get("data", {}).get("message_id")
        if message_id:
            # save message_id
            repo.message_id = message_id
            db.session.commit()
            pin_url = f"{bot.host}/open-apis/im/v1/pins"
            pin_result = bot.post(pin_url, json={"message_id": message_id}).json()
            logging.info("debug pin_result %r", pin_result)
            first_message_result = bot.reply(
                message_id,
                # 第一条话题消息，直接放repo_url
                FeishuTextMessage(f'<at user_id="all">所有人</at>\n{repo_url}'),
                reply_in_thread=True,
            ).json()
            logging.info("debug first_message_result %r", first_message_result)
        # 一共有3个result需要存到imaction里面
        return [result, pin_result, first_message_result]
    return False
