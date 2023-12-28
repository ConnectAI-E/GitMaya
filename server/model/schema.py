import json
import logging
from datetime import datetime

import bson
from app import db
from sqlalchemy import BINARY, String, text


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


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(ObjID(12), primary_key=True)
    openid = db.Column(db.String(128), nullable=True, comment="外部用户ID")
    name = db.Column(db.String(128), nullable=True, comment="用户名")
    extra = db.Column(
        JSONStr(1024), nullable=True, server_default=text("'{}'"), comment="用户其他字段"
    )
    status = db.Column(db.Integer, nullable=True, default=0, server_default=text("0"))
    created = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    modified = db.Column(
        db.TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
