import json
import logging
import os
from functools import wraps

from connectai.lark.sdk import Bot
from model.schema import (
    BindUser,
    ChatGroup,
    IMAction,
    IMApplication,
    IMEvent,
    Issue,
    ObjID,
    PullRequest,
    Repo,
    Team,
    TeamMember,
    db,
)
from sqlalchemy import or_
from utils.constant import GitHubPermissionError

# def get_topic_type_by_message_id(message_id):
#     """根据message_id获取话题类型和话题id(root_id)"""
#     results = (
#         db.session.query(GitObjectMessageIdRelation)
#         .filter(GitObjectMessageIdRelation.message_id == message_id)
#         .first()
#     )
#     # 判断results的repo_id,issue_id,pul_request_id 是否为否空来判断topic_tupe
#     topic_type = None
#     if results.repo_id:
#         return "repo", results.repo_id
#     elif results.issue_id:
#         return "issue", results.issue_id
#     elif results.pull_request_id:
#         return "pull_request", results.pull_request_id


def get_repo_id_by_chat_group(chat_id):
    chat_group = (
        db.session.query(ChatGroup)
        .filter(
            ChatGroup.chat_id == chat_id,
            ChatGroup.status == 0,
        )
        .first()
    )

    return chat_group


def get_repo_name_by_repo_id(repo_id):
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
            Repo.status == 0,
        )
        .first()
    )
    return repo.name


def get_bot_by_application_id(app_id):
    application = (
        db.session.query(IMApplication)
        .filter(
            or_(
                IMApplication.app_id == app_id,
                IMApplication.id == app_id,
            )
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


def get_git_object_by_message_id(message_id):
    issue = (
        db.session.query(Issue)
        .filter(
            Issue.message_id == message_id,
        )
        .first()
    )
    if issue:
        return None, issue, None
    pr = (
        db.session.query(PullRequest)
        .filter(
            PullRequest.message_id == message_id,
        )
        .first()
    )
    if pr:
        return None, None, pr
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.message_id == message_id,
        )
        .first()
    )
    if repo:
        return repo, None, None

    return None, None, None


def with_authenticated_github():
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            1. 这个装饰器用来统一处理错误消息
            2. github rest api调用出错的时候抛出异常
            3. 这个装饰器捕获特定的异常，给操作者特定的报错消息
            """
            try:
                return func(*args, **kwargs)
            except GitHubPermissionError as e:
                try:
                    from .manage import send_manage_fail_message

                    host = os.environ.get("DOMAIN")
                    send_manage_fail_message(
                        f"[请点击绑定GitHub账号后重试]({host}/api/github/oauth)",
                        app_id,
                        message_id,
                        content,
                        raw_message,
                    )
                except Exception as e:
                    logging.error(e)
            except Exception as e:
                raise e

        return wrapper

    return decorate


def with_lark_storage(event_type="message"):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            1. 按默认的规则，args[-3:]  message_id/card_event_token, message_content/card_event, raw_message/raw_card_event
            2. 可以尝试读取message_id + message_content存 event数据库
            3. result = func(*args, **kwargs)
            4. result默认当成数组处理，然后，就可以把result的每一项存action数据表
            """
            event_id = None
            try:
                app_id, message_id, content, raw_message = args[-4:]
                application = (
                    db.session.query(IMApplication)
                    .filter(
                        IMApplication.app_id == app_id,
                    )
                    .first()
                )
                if "om_" in message_id and application:
                    event_id = ObjID.new_id()
                    db.session.add(
                        IMEvent(
                            id=event_id,
                            application_id=application.id,
                            event_id=message_id,
                            event_type=event_type,  # TODO 这里要不只存parser里面的command算了
                            content=json.dumps(content)[:128],
                            extra=raw_message,
                        )
                    )
                    db.session.commit()
            except Exception as e:
                logging.error(e)

            result = func(*args, **kwargs)

            try:
                # try save result
                if event_id:
                    results = result if isinstance(result, list) else [result]
                    for action_result in results:
                        message_id = (
                            action_result.get("data", {}).get("message_id", "")
                            if isinstance(action_result, dict)
                            else ""
                        )
                        db.session.add(
                            IMAction(
                                id=ObjID.new_id(),
                                event_id=event_id,
                                message_id=message_id,
                                action_type=func.__name__,
                                content=json.dumps(action_result)[:128],
                                extra=action_result,
                            )
                        )
                    db.session.commit()
            except Exception as e:
                logging.error(e)
            return result

        return wrapper

    return decorate


def with_authenticated_github1():
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            判断操用户是否绑定github有权限操作卡片，没有则发出对应的失败消息卡片
            """
            logging.info("---with_authenticated_github---")
            #     team = (
            #         db.session.query(Team)
            #         .filter(
            #             Team.app_id == app_id,
            #         )
            #         .first()
            #     )

            #     team_member = (
            #         db.session.query(TeamMember)
            #         .filter(
            #             TeamMember.team_id == team.id,
            #             TeamMember.im_user_id == open_id,
            #             TeamMember.status == 0,
            #             BindUser.status == 0,
            #         )
            #         .first()
            #     )
            #     bind_user = (
            #         db.session.query(BindUser)
            #         .filter(
            #             BindUser.user_id == team_member.code_user_id,
            #             BindUser.platform == "github",
            #             BindUser.status == 0,
            #         )
            #         .first()
            #     )
            #     access_token = bind_user.access_token

            # logging.info(f"access_token: {access_token}")
            try:
                host = os.getenv("VIRTUAL_HOST")

                response = func(*args, **kwargs)
                logging.error(f"---with_authenticated_github--- response: {response}")
                if response["code"] == 200:
                    return

                # 找到用户的open_id
                # 指令消息体
                if len(args) > 4:
                    app_id, message_id, content, raw_message, open_id = args[-4:]
                    # open_id = raw_message["event"]["sender"]["sender_id"].get(
                    #     "open_id", None
                    # )
                # 点击消息体
                else:
                    app_id, message_id, raw_message = args[-3:]
                    # open_id = raw_message.get("open_id", None)
                if response["code"] == 0:
                    from lark.chat import send_chat_failed_tip

                    return send_chat_failed_tip.delay(
                        f"[请点击绑定GitHub账号后重试]({host}/api/github/oauth)",
                        app_id,
                        message_id,
                        raw_message,
                        *args,
                        **kwargs,
                    )

            except Exception as e:
                logging.error(e)

        return wrapper

    return decorate
