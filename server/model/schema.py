import json
import logging
from datetime import datetime

import bson
from app import db
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
            if not isinstance(value, bytes):
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
    id = db.Column(ObjID(12), primary_key=True)
    status = db.Column(db.Integer, nullable=True, default=0, server_default=text("0"))
    created = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    modified = db.Column(
        db.TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(Base):
    __tablename__ = "user"
    email = db.Column(db.String(128), nullable=True, comment="邮箱,这里考虑一下如何做唯一的用户")
    telephone = db.Column(db.String(128), nullable=True, comment="手机号")
    name = db.Column(db.String(128), nullable=True, comment="用户名")
    avatar = db.Column(db.String(128), nullable=True, comment="头像")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="用户其他字段"
    )


class Account(User):
    passwd = Column(
        String(128), nullable=True, server_default=text("''"), comment="登录密码"
    )


class BindUser(Base):
    __tablename__ = "bint_user"
    user_id = Column(ObjID(12), ForeignKey("user.id"), nullable=True, comment="用户ID")
    # 这里如果是飞书租户，可能会有不同的name等，但是在github这边不管是哪一个org，都是一样的
    # 这里如何统一？
    # 是不是说这里暂时不需要这个platform_id，还是说这个字段为空就好？
    platform_id = Column(
        ObjID(12), ForeignKey("im_platform.id"), nullable=True, comment="平台"
    )
    unionid = db.Column(db.String(128), nullable=True, comment="飞书的unionid")

    # 这里还是用platform标记一下
    platform = db.Column(db.String(128), nullable=True, comment="平台：github/lark")
    email = db.Column(db.String(128), nullable=True, comment="邮箱")
    name = db.Column(db.String(128), nullable=True, comment="用户名")
    avatar = db.Column(db.String(128), nullable=True, comment="头像")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="用户其他字段"
    )


class Team(Base):
    __tablename__ = "team"
    user_id = Column(ObjID(12), ForeignKey("user.id"), nullable=True, comment="用户ID")
    code_platform_id = Column(
        ObjID(12), ForeignKey("code_platform.id"), nullable=True, comment="代码平台"
    )
    im_platform_id = Column(
        ObjID(12), ForeignKey("im_platform.id"), nullable=True, comment="协同平台"
    )

    name = db.Column(db.String(128), nullable=True, comment="名称")
    description = db.Column(db.String(1024), nullable=True, comment="描述")
    extra = db.Column(
        JSONStr(1024),
        nullable=True,
        server_default=text("'{}'"),
        comment="其他字段，可能有一些前期没想好的配置项放这里",
    )


class TeamMember(Base):
    __tablename__ = "team_member"
    team_id = Column(ObjID(12), ForeignKey("team.id"), nullable=True, comment="属于哪一个组")
    code_user_id = Column(
        ObjID(12),
        ForeignKey("bind_user.id"),
        nullable=True,
        comment="从code_platform关联过来的用户",
    )
    im_user_id = Column(
        ObjID(12),
        ForeignKey("bind_user.id"),
        nullable=True,
        comment="从im_platform关联过来的用户",
    )


class CodePlatform(Base):
    __tablename__ = "code_platform"
    name = db.Column(db.String(128), nullable=True, comment="名称")
    description = db.Column(db.String(1024), nullable=True, comment="描述")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class Repo(Base):
    __tablename__ = "repo"
    code_platform_id = Column(
        ObjID(12), ForeignKey("code_platform.id"), nullable=True, comment="属于哪一个org"
    )
    application_id = Column(
        ObjID(12),
        ForeignKey("code_application.id"),
        nullable=True,
        comment="哪一个application_id",
    )
    name = db.Column(db.String(128), nullable=True, comment="名称")
    description = db.Column(db.String(1024), nullable=True, comment="描述")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class RepoUser(Base):
    __tablename__ = "repo_user"
    code_platform_id = Column(
        ObjID(12), ForeignKey("code_platform.id"), nullable=True, comment="属于哪一个org"
    )
    application_id = Column(
        ObjID(12),
        ForeignKey("code_application.id"),
        nullable=True,
        comment="哪一个application_id",
    )
    bind_user_id = Column(
        ObjID(12), ForeignKey("bind_user.id"), nullable=True, comment="项目协作者"
    )


class IMPlatform(Base):
    __tablename__ = "im_platform"
    tenant_key = db.Column(db.String(128), nullable=True, comment="飞书租户id")
    name = db.Column(db.String(128), nullable=True, comment="名称")
    description = db.Column(db.String(1024), nullable=True, comment="描述")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class CodeApplication(Base):
    __tablename__ = "code_application"
    platform_id = Column(
        ObjID(12), ForeignKey("code_platform.id"), nullable=True, comment="代码平台"
    )
    installation_id = db.Column(db.String(128), nullable=True, comment="安装id")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class CodeEvent(Base):
    __tablename__ = "code_event"
    application_id = Column(
        ObjID(12), ForeignKey("code_application.id"), nullable=True, comment="应用id"
    )
    event_id = db.Column(db.String(128), nullable=True, comment="event_id")
    event_type = db.Column(db.String(128), nullable=True, comment="event_type")
    content = db.Column(db.String(128), nullable=True, comment="主要内容")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class CodeAction(Base):
    __tablename__ = "code_action"
    event_id = Column(
        ObjID(12), ForeignKey("code_event.id"), nullable=True, comment="事件ID"
    )
    action_type = db.Column(
        db.String(128), nullable=True, comment="action_type: 主要是飞书那边的消息等"
    )
    content = db.Column(db.String(128), nullable=True, comment="主要内容")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class IMApplication(Base):
    __tablename__ = "im_application"
    platform_id = Column(
        ObjID(12), ForeignKey("code_platform.id"), nullable=True, comment="协同平台"
    )
    app_id = db.Column(db.String(128), nullable=True, comment="app_id")
    app_secret = db.Column(db.String(128), nullable=True, comment="app_id")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class IMEvent(Base):
    __tablename__ = "im_event"
    application_id = Column(
        ObjID(12), ForeignKey("im_application.id"), nullable=True, comment="应用id"
    )
    event_id = db.Column(db.String(128), nullable=True, comment="event_id")
    event_type = db.Column(db.String(128), nullable=True, comment="event_type")
    content = db.Column(db.String(128), nullable=True, comment="主要内容")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class IMAction(Base):
    __tablename__ = "im_action"
    event_id = Column(
        ObjID(12), ForeignKey("im_event.id"), nullable=True, comment="事件ID"
    )
    action_type = db.Column(
        db.String(128), nullable=True, comment="action_type: 主要是github那边的动作等"
    )
    content = db.Column(db.String(128), nullable=True, comment="主要内容")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


class ChatGroup(Base):
    __tablename__ = "chat_group"
    repo_id = Column(ObjID(12), ForeignKey("repo.id"), nullable=True, comment="属于哪一个项目")
    im_application_id = Column(
        ObjID(12), ForeignKey("code_application.id"), nullable=True, comment="哪一个项目创建的"
    )
    chat_id = db.Column(db.String(128), nullable=True, comment="chat_id")
    name = db.Column(db.String(128), nullable=True, comment="群名称")
    description = db.Column(db.String(128), nullable=True, comment="群描述")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="其他字段"
    )


if __name__ == "__main__":
    from app import app

    with app.app_context():
        db.create_all()
