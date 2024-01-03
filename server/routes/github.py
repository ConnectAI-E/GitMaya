import os

from app import app
from flask import Blueprint, abort, redirect, request, session
from model.team import create_code_application, create_team
from utils.auth import authenticated
from utils.github.application import (
    get_installation_info,
    get_installation_token,
    get_jwt,
    verify_github_signature,
)
from utils.user import register

bp = Blueprint("github", __name__, url_prefix="/api/github")


@bp.route("/install", methods=["GET"])
@authenticated
def github_install():
    """Install GitHub App.

    Redirect to GitHub App installation page.
    """
    installation_id = request.args.get("installation_id", None)
    if installation_id is None:
        return redirect(
            f"https://github.com/apps/{os.environ.get('GITHUB_APP_NAME')}/installations/new"
        )

    # 创建 Team
    print(f"installation_id {installation_id}")

    jwt = get_jwt(
        os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH"),
        os.environ.get("GITHUB_APP_ID"),
    )
    installation_token = get_installation_token(jwt, installation_id)
    if installation_token is None:
        app.logger.error("Failed to get installation token.")
        return "Failed to get installation token."

    app_info = get_installation_info(jwt, installation_id)
    if app_info is None:
        app.logger.error("Failed to get installation info.")
        return "Failed to get installation info."

    # 判断安装者的身份是用户还是组织
    type = app_info["account"]["type"]
    if type == "user":
        app.logger.error("User is not allowed to install.")
        # TODO: 定义与前端的交互数据格式
        return "User is not allowed to install."

    team = create_team(app_info)
    code_application = create_code_application(team.id, installation_id)

    return app_info


@bp.route("/oauth", methods=["GET"])
def github_register():
    """GitHub OAuth register.

    If not `code`, redirect to GitHub OAuth page.
    If `code`, register by code.
    """
    code = request.args.get("code", None)

    if code is None:
        return redirect(
            f"https://github.com/login/oauth/authorize?client_id={os.environ.get('GITHUB_CLIENT_ID')}"
        )

    # 通过 code 注册；如果 user 已经存在，则一样会返回 user_id
    user_id = register(code)
    if user_id is None:
        return "Failed to register by code."

    # 保存用户注册状态
    session["user_id"] = user_id

    return "Success!"


@bp.route("/hook", methods=["POST"])
@verify_github_signature(os.environ.get("GITHUB_WEBHOOK_SECRET"))
def github_hook():
    """Receive GitHub webhook."""

    x_github_event = request.headers.get("x-github-event", None)

    app.logger.info(x_github_event)

    app.logger.debug(request.json)

    return "Receive Success!"


app.register_blueprint(bp)
