from enum import Enum


class ErrorMsg(Enum):
    APP_NOT_FOUND = "找不到对应的应用"
    INVALID_INPUT = "输入无效"
    OPERATION_FAILED = "操作失败"


class SuccessMsg(Enum):
    OPERATION_SUCCESS = "操作成功"
