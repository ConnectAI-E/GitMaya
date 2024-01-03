import json
import os

from app import app
from flask import Blueprint, abort, jsonify, make_response, redirect, request, session
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

    jwt = get_jwt(
        os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH"),
        os.environ.get("GITHUB_APP_ID"),
    )
    installation_token = get_installation_token(jwt, installation_id)
    try:
        if installation_token is None:
            app.logger.error("Failed to get installation token.")
            raise Exception("Failed to get installation token.")

        app_info = get_installation_info(jwt, installation_id)
        if app_info is None:
            app.logger.error("Failed to get installation info.")
            raise Exception("Failed to get installation info.")

        # 判断安装者的身份是用户还是组织
        type: str = app_info["account"]["type"]
        if type.lower() == "user":
            app.logger.error("User is not allowed to install.")
            # TODO: 定义与前端的交互数据格式
            raise Exception("User is not allowed to install.")

        team = create_team(app_info)
        code_application = create_code_application(team.id, installation_id)
    except Exception as e:
        # 返回错误信息
        app_info = str(e)

    # TODO: 加入后台任务

    return make_response(
        """
<script>
try {
  window.opener.postMessage("""
        + json.dumps(dict(event="installation", data=app_info))
        + """, '*')
  setTimeout(() => window.close(), 3000)
} catch(e) {
  console.error(e)
  location.replace('/')
}
</script>
                                     """,
        {"Content-Type": "text/html"},
    )


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
    # if user_id is None:
    #     return jsonify({"message": "Failed to register."}), 500

    # 保存用户注册状态
    if user_id:
        session["user_id"] = user_id

    return make_response(
        """
<script>
try {
  window.opener.postMessage("""
        + json.dumps(dict(event="oauth", data={"user_id": user_id}))
        + """, '*')
  setTimeout(() => window.close(), 3000)
} catch(e) {
  console.error(e)
  location.replace('/')
}
</script>
                                     """,
        {"Content-Type": "text/html"},
    )


@bp.route("/hook", methods=["POST"])
@verify_github_signature(os.environ.get("GITHUB_WEBHOOK_SECRET"))
def github_hook():
    """Receive GitHub webhook."""

    x_github_event = request.headers.get("x-github-event", None)

    app.logger.info(x_github_event)

    app.logger.debug(request.json)

    return "Receive Success!"


app.register_blueprint(bp)
