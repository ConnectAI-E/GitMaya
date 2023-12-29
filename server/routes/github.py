import logging
import os

from app import app
from flask import Blueprint, abort, redirect, request, session
from utils.auth import authenticated

from server.utils.github.github import (
    get_installation_token,
    get_jwt,
    verify_github_signature,
)
from server.utils.user import register

bp = Blueprint("github", __name__, url_prefix="/api/github")


@bp.route("/install", methods=["GET"])
@authenticated
def github_install():
    """Install GitHub App.

    If not `installation_id`, redirect to install page.
    If `installation_id`, get installation token.

    If `code`, register by code.
    """
    installation_id = request.args.get("installation_id", None)

    if installation_id is None:
        return redirect(
            f"https://github.com/apps/{os.environ.get('GITHUB_APP_NAME')}/installations/new"
        )

    logging.debug(f"installation_id: {installation_id}")

    jwt = get_jwt(
        os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH"),
        os.environ.get("GITHUB_APP_ID"),
    )

    installation_token = get_installation_token(jwt, installation_id)
    if installation_token is None:
        logging.debug("Failed to get installation token.")

        # TODO: 统一解决各类 http 请求失败的情况
        abort(500)
    logging.debug(f"installation_token: {installation_token}")

    return "Success!"


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

    user_id = register(code)
    if user_id is None:
        return "Failed to register by code."

    session["user_id"] = user_id

    # TODO: 统一的返回格式
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
