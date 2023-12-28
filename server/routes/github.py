import os

from app import app
from flask import Blueprint, abort, redirect, request
from utils.github import get_installation_token, get_jwt, register_by_code

bp = Blueprint("github", __name__, url_prefix="/api/github")


@bp.route("/install", methods=["GET"])
def github_install():
    installation_id = request.args.get("installation_id", None)

    if installation_id is None:
        return redirect(
            f"https://github.com/apps/{os.environ.get('GITHUB_APP_NAME')}/installations/new"
        )

    print(f"installation_id: {installation_id}")

    jwt = get_jwt(
        os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH"),
        os.environ.get("GITHUB_APP_ID"),
    )

    installation_token = get_installation_token(jwt, installation_id)
    if installation_token is None:
        print("Failed to get installation token.")

        # TODO: 统一解决各类 http 请求失败的情况
        abort(500)
    print(f"installation_token: {installation_token}")

    # 如果有 code 参数，则为该用户注册
    code = request.args.get("code", None)
    if code is not None:
        print(f"code: {code}")

        user_token = register_by_code(code)
        if user_token is None:
            print("Failed to register by code.")
            abort(500)

        print(f"user_token: {user_token}")

    return "Success!"


app.register_blueprint(bp)
