import logging
import os

from app import app
from flask import Blueprint, abort, redirect, request, session
from model.schema import Team
from utils.auth import authenticated
from utils.github.common import get_installation_token, get_jwt, verify_github_signature
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


@bp.route("/register", methods=["GET"])
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

    logging.info(x_github_event)

    logging.debug(request.json)

    return "Receive Success!"


app.register_blueprint(bp)
