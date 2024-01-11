from enum import Enum


class ErrorMsg(Enum):
    APP_NOT_FOUND = "找不到对应的应用"
    REPO_CHAT_GROUP_NOT_FOUND = "找不到项目群"
    REPO_NOT_FOUND = "找不到项目群对应项目"
    INVALID_INPUT = "输入无效"
    OPERATION_FAILED = "操作失败"


class SuccessMsg(Enum):
    OPERATION_SUCCESS = "操作成功"


class TopicType(Enum):
    REPO = "repo"
    ISSUE = "issue"
    PR = "pull_request"
    PULL_REQUEST = "pull_request"
    CHAT = "chat"


class GitHubPermissionError(Exception):
    pass
