from app import app, db
from flask import abort
from model.schema import BindUser, ObjID, User
from utils.github.account import get_email, get_user_info
from utils.github.application import oauth_by_code


def register(code: str) -> str | None:
    """GitHub OAuth register.

    If `code`, register by code.
    """

    oauth_info = oauth_by_code(code)  # 获取 access token
    if oauth_info is None:
        abort(500)

    access_token = oauth_info.get("access_token", None)[0]  # 这里要考虑取哪个，为什么会有多个？

    # 使用 oauth_info 中的 access_token 获取用户信息
    user_info = get_user_info(access_token)

    # 查询 github_id 是否已经存在，若存在，则返回 user_id
    github_id = user_info.get("id", None)
    if github_id is not None:
        user = User.query.filter_by(unionid=github_id).first()
        if user is not None:
            return user.id

    email = get_email(access_token)

    new_user = User(
        id=ObjID.new_id(),
        unionid=github_id,
        email=email,  # 这里的邮箱其实是公开邮箱，可能会获取不到 TODO: 换成使用用户邮箱 API 来获取
        name=user_info.get("login", None),
        avatar=user_info.get("avatar_url", None),
        extra=user_info,
    )

    db.session.add(new_user)
    db.session.flush()

    new_bind_user = BindUser(
        id=ObjID.new_id(),
        user_id=new_user.id,
        platform="github",
        email=email,
        name=user_info.get("login", None),
        avatar=user_info.get("avatar_url", None),
        access_token=access_token,
        extra=oauth_info,
    )

    db.session.add(new_bind_user)

    db.session.commit()

    return new_user.id
