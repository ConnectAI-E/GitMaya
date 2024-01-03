import os

from celery_app import celery
from model.schema import db
from utils.github.application import get_installation_token, get_jwt
from utils.github.organization import get_org_members


@celery.task()
def pull_repo(org_name: str, installation_id: str, application_id: str):
    """Pull repo from GitHub, build Repo and RepoUser."""
    # 获取 jwt 和 installation_token

    installation_token: str = get_installation_token(
        get_jwt(
            os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH"),
            os.environ.get("GITHUB_APP_ID"),
        ),
        installation_id,
    )  # TODO: 这里有一个遗留问题：installation_token 有一小时的期限
    # 解决方案是在 utils.github.application 中增加一个类，用于统一管理 jwt 和 installation_token

    if installation_token is None:
        raise Exception("Failed to get installation token.")  # TODO: 统一处理 celery 报错？

    # 拉取所有组织成员，创建 BindUser
    members = get_org_members(org_name, installation_token)
    if members is None or not isinstance(members, list):
        raise Exception("Failed to get org members.")

    for member in members:
        # 检查是否已经存在（其实只有一个人会重复？）
        pass

    # 拉取所有组织仓库，创建 Repo
    # 给每个仓库创建 RepoUser

    pass
