from app import app, db
from flask import abort
from model.schema import BindUser, ObjID, User
from utils.github.account import get_email, get_user_info
from utils.github.application import oauth_by_code


def register(code: str) -> str | None:
    """GitHub OAuth register.

    If `code`, register by code.

    Args:
        code (str): The code of the GitHub OAuth.

    Returns:
        str | None: The id of the user.
    """

    oauth_info = oauth_by_code(code)  # 获取 access token
    if oauth_info is None:
        abort(500)

    access_token = oauth_info.get("access_token", None)[0]  # 这里要考虑取哪个，为什么会有多个？
    # TODO: 预备好对 user_access_token 的刷新处理

    # 使用 oauth_info 中的 access_token 获取用户信息
    user_info = get_user_info(access_token)

    # 查询 github_id 是否已经存在，若存在，则刷新 access_token，返回 user_id
    github_id = user_info.get("id", None)

    email = get_email(access_token)

    new_user_id, _ = create_github_user(
        github_id=github_id,
        name=user_info.get("name", None),
        email=email,
        avatar=user_info.get("avatar_url", None),
        access_token=access_token,
        extra={"user_info": user_info, "oauth_info": oauth_info},
    )

    return new_user_id


def create_github_user(
    github_id: str,
    name: str,
    email: str,
    avatar: str,
    access_token: str = None,
    application_id: str = None,
    extra: dict = {},
) -> (str, str):
    """Create a GitHub user.

    Args:
        name (str): The name of the user.
        email (str): The email of the user.
        avatar (str): The avatar of the user.
        extra (dict): The extra of the user.

    Returns:
        str: The id of the user.
    """

    if github_id is not None:
        user = User.query.filter_by(unionid=github_id).first()
        if user is not None:
            bind_user = BindUser.query.filter_by(
                user_id=user.id, platform="github"
            ).first()

            if bind_user is None:
                raise Exception("Failed to get bind user.")

            # 刷新 access_token
            if access_token is not None:
                bind_user.access_token = access_token

            # 刷新 email
            if email is not None:
                bind_user.email = email

            if application_id is not None:
                bind_user.application_id = application_id

            db.session.commit()
            return user.id, bind_user.id

    new_user = User(
        id=ObjID.new_id(),
        unionid=github_id,
        email=email,
        name=name,
        avatar=avatar,
        extra=extra.get("user_info", None),
    )

    db.session.add(new_user)
    db.session.flush()

    new_bind_user = BindUser(
        id=ObjID.new_id(),
        user_id=new_user.id,
        platform="github",
        email=email,
        name=name,
        avatar=avatar,
        access_token=access_token,
        application_id=application_id,
        extra=extra.get("oauth_info", None),
    )

    db.session.add(new_bind_user)

    db.session.commit()

    return new_user.id, new_bind_user.id
