import copy
import json
import logging
from datetime import datetime
from time import time

import bson
import click
from app import app, db
from flask.cli import with_appcontext
from flask.json.provider import DefaultJSONProvider
from sqlalchemy import BINARY, ForeignKey, String, text


class ObjID(BINARY):
    """基于bson.ObjectId用于mysql主键的自定义类型"""

    def bind_processor(self, dialect):
        def processor(value):
            return (
                bson.ObjectId(value).binary if bson.ObjectId.is_valid(value) else value
            )

        return processor

    def result_processor(self, dialect, coltype):
        def processor(value):
            if value and not isinstance(value, bytes):
                value = bytes(value)
            return str(bson.ObjectId(value)) if bson.ObjectId.is_valid(value) else value

        return processor

    @staticmethod
    def new_id():
        return str(bson.ObjectId())

    @staticmethod
    def is_valid(value):
        return bson.ObjectId.is_valid(value)


class JSONStr(String):
    """自动转换 str 和 dict 的自定义类型"""

    def bind_processor(self, dialect):
        def processor(value):
            try:
                if isinstance(value, str) and (value[0] == "%" or value[-1] == "%"):
                    # 使用like筛选的情况
                    return value
                return json.dumps(value, ensure_ascii=False)
            except Exception as e:
                logging.exception(e)
                return value

        return processor

    def result_processor(self, dialect, coltype):
        def processor(value):
            try:
                return json.loads(value)
            except Exception as e:
                logging.exception(e)
                return value

        return processor

    @staticmethod
    def is_valid(value):
        try:
            json.loads(value)
            return True
        except Exception as e:
            logging.exception(e)
            return False


class Base(db.Model):
    __abstract__ = True
    id = db.Column(ObjID(12), primary_key=True)
    status = db.Column(db.Integer, nullable=True, default=0, server_default=text("0"))
    created = db.Column(
        db.TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    modified = db.Column(
        db.TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="修改时间",
    )


class User(Base):
    __tablename__ = "user"
    unionid = db.Column(
        db.String(128), nullable=True, comment="GitHub ID/lark union_id, 作为唯一标识"
    )
    email = db.Column(db.String(128), nullable=True, comment="邮箱,这里考虑一下如何做唯一的用户")
    telephone = db.Column(db.String(128), nullable=True, comment="手机号")
    name = db.Column(db.String(128), nullable=True, comment="用户名")
    avatar = db.Column(db.String(256), nullable=True, comment="头像")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="用户其他字段"
    )


class Account(User):
    passwd = db.Column(
        db.String(128), nullable=True, server_default=text("''"), comment="登录密码"
    )


class BindUser(Base):
    __tablename__ = "bind_user"
    user_id = db.Column(ObjID(12), ForeignKey("user.id"), nullable=True, comment="用户ID")
    # 这里还是用platform标记一下
    platform = db.Column(db.String(128), nullable=True, comment="平台：github/lark")
    # 实际关联的，可能是code_application.id或者im_application.id
    application_id = db.Column(ObjID(12), nullable=True, comment="应用ID")
    unionid = db.Column(db.String(128), nullable=True, comment="飞书的unionid")
    openid = db.Column(db.String(128), nullable=True, comment="飞书的openid")

    email = db.Column(db.String(128), nullable=True, comment="邮箱")
    name = db.Column(db.String(128), nullable=True, comment="用户名")
    avatar = db.Column(db.String(256), nullable=True, comment="头像")
    access_token = db.Column(
        db.String(128), nullable=True, comment="GitHub access_token"
    )
    refresh_token = db.Column(
        db.String(128), nullable=True, comment="GitHub refresh_token"
    )
    expire_time = db.Column(db.Integer, nullable=True, comment="GitHub token过期时间 时间戳")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="用户其他字段"
    )


class Team(Base):
    __tablename__ = "team"
    user_id = db.Column(ObjID(12), ForeignKey("user.id"), nullable=True, comment="用户ID")
    # 移除从team到application_id的关联，使用application.team_id关联

    name = db.Column(
        db.String(128), nullable=True, comment="名称"
    )  # 同时也是 GitHub Org 的 name
    description = db.Column(db.String(1024), nullable=True, comment="描述")
    extra = db.Column(
        JSONStr(2048),
        nullable=True,
        server_default=text("'{}'"),
        comment="其他字段，可能有一些前期没想好的配置项放这里",
    )


class TeamMember(Base):
    __tablename__ = "team_member"
    team_id = db.Column(
        ObjID(12), ForeignKey("team.id"), nullable=True, comment="属于哪一个组"
    )
    code_user_id = db.Column(
        ObjID(12),
        ForeignKey("bind_user.id"),
        nullable=True,
        comment="从code_application关联过来的用户",
    )
    im_user_id = db.Column(
        ObjID(12),
        ForeignKey("bind_user.id"),
        nullable=True,
        comment="从im_application关联过来的用户",
    )


class Repo(Base):
    __tablename__ = "repo"
    application_id = db.Column(
        ObjID(12),
        ForeignKey("code_application.id"),
        nullable=True,
        comment="哪一个application_id",
    )
    owner_bind_id = db.Column(
        ObjID(12), ForeignKey("bind_user.id"), nullable=True, comment="项目所有者"
    )
    repo_id = db.Column(db.String(128), nullable=True, comment="repo_id")
    name = db.Column(db.String(128), nullable=True, comment="名称")
    description = db.Column(db.String(1024), nullable=True, comment="描述")
    message_id = db.Column(db.String(128), nullable=True, comment="message_id")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class RepoUser(Base):
    __tablename__ = "repo_user"
    application_id = db.Column(
        ObjID(12),
        ForeignKey("code_application.id"),
        nullable=True,
        comment="哪一个application_id",
    )
    repo_id = db.Column(
        ObjID(12), ForeignKey("repo.id"), nullable=True, comment="属于哪一个项目"
    )
    bind_user_id = db.Column(
        ObjID(12), ForeignKey("bind_user.id"), nullable=True, comment="项目协作者"
    )


class CodeApplication(Base):
    __tablename__ = "code_application"
    team_id = db.Column(
        ObjID(12), ForeignKey("team.id"), nullable=True, comment="属于哪一个组"
    )
    platform = db.Column(db.String(128), nullable=True, comment="平台：github")
    installation_id = db.Column(db.String(128), nullable=True, comment="安装id")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class CodeEvent(Base):
    __tablename__ = "code_event"
    application_id = db.Column(
        ObjID(12), ForeignKey("code_application.id"), nullable=True, comment="应用id"
    )
    event_id = db.Column(db.String(128), nullable=True, comment="event_id")
    event_type = db.Column(db.String(128), nullable=True, comment="event_type")
    content = db.Column(db.String(128), nullable=True, comment="主要内容")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class CodeAction(Base):
    __tablename__ = "code_action"
    event_id = db.Column(
        ObjID(12), ForeignKey("code_event.id"), nullable=True, comment="事件ID"
    )
    action_type = db.Column(
        db.String(128), nullable=True, comment="action_type: 主要是飞书那边的消息等"
    )
    content = db.Column(db.String(128), nullable=True, comment="主要内容")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class IMApplication(Base):
    __tablename__ = "im_application"
    team_id = db.Column(
        ObjID(12), ForeignKey("team.id"), nullable=True, comment="属于哪一个组"
    )
    platform = db.Column(db.String(128), nullable=True, comment="平台：lark")
    app_id = db.Column(db.String(128), nullable=True, comment="app_id")
    app_secret = db.Column(db.String(128), nullable=True, comment="app_id")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class IMEvent(Base):
    __tablename__ = "im_event"
    application_id = db.Column(
        ObjID(12), ForeignKey("im_application.id"), nullable=True, comment="应用id"
    )
    event_id = db.Column(db.String(128), nullable=True, comment="event_id")
    event_type = db.Column(db.String(128), nullable=True, comment="event_type")
    content = db.Column(db.String(128), nullable=True, comment="主要内容")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class IMAction(Base):
    __tablename__ = "im_action"
    event_id = db.Column(
        ObjID(12), ForeignKey("im_event.id"), nullable=True, comment="事件ID"
    )
    action_type = db.Column(
        db.String(128), nullable=True, comment="action_type: 主要是github那边的动作等"
    )
    message_id = db.Column(db.String(128), nullable=True, comment="message_id")
    content = db.Column(db.String(128), nullable=True, comment="主要内容")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class ChatGroup(Base):
    __tablename__ = "chat_group"
    repo_id = db.Column(
        ObjID(12), ForeignKey("repo.id"), nullable=True, comment="属于哪一个项目"
    )
    im_application_id = db.Column(
        ObjID(12), ForeignKey("im_application.id"), nullable=True, comment="哪一个项目创建的"
    )
    chat_id = db.Column(db.String(128), nullable=True, comment="chat_id")
    name = db.Column(db.String(128), nullable=True, comment="群名称")
    description = db.Column(db.String(128), nullable=True, comment="群描述")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class Issue(Base):
    __tablename__ = "issue"
    repo_id = db.Column(
        ObjID(12),
        ForeignKey("repo.id"),
        nullable=True,
        comment="哪一个repo_id",
    )
    name = db.Column(db.String(128), nullable=True, comment="名称")
    description = db.Column(db.String(1024), nullable=True, comment="描述")
    message_id = db.Column(db.String(128), nullable=True, comment="message_id")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class PullRequest(Base):
    __tablename__ = "pull_request"
    repo_id = db.Column(
        ObjID(12),
        ForeignKey("repo.id"),
        nullable=True,
        comment="哪一个repo_id",
    )
    name = db.Column(db.String(128), nullable=True, comment="名称")
    description = db.Column(db.String(1024), nullable=True, comment="描述")
    message_id = db.Column(db.String(128), nullable=True, comment="message_id")
    extra = db.Column(
        JSONStr(2048), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class GitObjectMessageIdRelation(db.Model):
    __abstract__ = True
    __tablename__ = "git_object_message_id_relation"
    __table_args__ = {"info": dict(is_view=True)}
    repo_id = db.Column(ObjID(12), nullable=True, comment="repo.id")
    issue_id = db.Column(ObjID(12), nullable=True, comment="issue.id")
    pull_request_id = db.Column(ObjID(12), nullable=True, comment="pull_request.id")
    message_id = db.Column(db.String(128), nullable=True, comment="message_id")


class CustomJsonProvider(DefaultJSONProvider):
    @staticmethod
    def default(value):
        if isinstance(value, db.Model):
            value = copy.deepcopy(value.__dict__)
            del value["_sa_instance_state"]
            return value
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)


app.json_provider_class = CustomJsonProvider
app.json = CustomJsonProvider(app)


# create command function
@click.command(name="create")
@with_appcontext
def create():
    db.create_all()
    try:
        connection = db.session.connection()
        result = connection.execute(
            text(
                """
create view `git_object_message_id_relation` as select * from (
select id as repo_id, null as issue_id, null as pull_request_id, message_id from `repo`
union all(select null as repo_id, id as issue_id, null as pull_request_id, message_id from `issue`)
union all(select null as repo_id, null as issue_id, id as pull_request_id, message_id from `pull_request`)
) as t
                                   """
            )
        )
    except Exception as e:
        logging.error(e)


# add command function to cli commands
app.cli.add_command(create)
