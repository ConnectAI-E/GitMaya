from app import app, db
from model.schema import BindUser, ObjID, User
from utils.github.common import get_user_info, oauth_by_code


def register(code: str) -> str | None:
    """GitHub OAuth register.

    If `code`, register by code.
    """

    oauth_info = oauth_by_code(code)  # 获取 access token

    access_token = oauth_info.get("access_token", None)[0]  # 这里要考虑取哪个，为什么会有多个？

    # 使用 oauth_info 中的 access_token 获取用户信息
    user_info = get_user_info(access_token)

    # 查询 github_id 是否已经存在，若存在，则返回 user_id
    github_id = user_info.get("id", None)
    if github_id is not None:
        user = User.query.filter_by(github_id=github_id).first()
        if user is not None:
            return user.id

    new_user = User(
        id=ObjID.new_id(),
        github_id=github_id,
        email=user_info.get(
            "email", None
        ),  # 这里的邮箱其实是公开邮箱，可能会获取不到 TODO: 换成使用用户邮箱 API 来获取
        name=user_info.get("login", None),
        avatar=user_info.get("avatar_url", None),
        extra=user_info,
    )

    db.session.add(new_user)
    db.session.commit()

    new_bind_user = BindUser(
        id=ObjID.new_id(),
        user_id=new_user.id,
        platform="github",
        email=user_info.get("email", None),
        avatar=user_info.get("avatar_url", None),
        extra=oauth_info,
    )

    db.session.add(new_bind_user)

    db.session.commit()

    return new_user.id
