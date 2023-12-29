from app import app, db
from model.schema import BindUser, User

from server.utils.github.github import oauth_by_code


def register(code: str) -> str | None:
    """GitHub OAuth register.

    If not `code`, redirect to GitHub OAuth page.
    If `code`, register by code.
    """

    oauth_info = oauth_by_code(code)

    user_info = oauth_info.get("user", None)

    # 使用 oauth_info 中的 access_token 获取用户信息

    new_user = User(
        email=user_info.get("email", None),
        name=user_info.get("login", None),  # TODO: 确认一下 login 和 name 哪个是唯一的
        avatar=user_info.get("avatar_url", None),
        extra=user_info,
    )

    db.session.add(new_user)

    new_bind_user = BindUser(
        user_id=new_user.id,
        platform="github",
        email=user_info.get("email", None),
        avatar=user_info.get("avatar_url", None),
        extra=oauth_info,
    )

    db.session.add(new_bind_user)

    db.session.commit()

    return new_user.id
