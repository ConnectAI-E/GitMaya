import logging
import os

from app import app
from flask import Blueprint, abort, redirect, request
from utils.github import get_installation_token, get_jwt, register_by_code

bp = Blueprint("github", __name__, url_prefix="/api/github")


@bp.route("/install", methods=["GET"])
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

    # 如果有 code 参数，则为该用户注册
    code = request.args.get("code", None)
    if code is not None:
        logging.debug(f"code: {code}")

        user_token = register_by_code(code)
        if user_token is None:
            logging.debug("Failed to register by code.")
            abort(500)

        logging.debug(f"user_token: {user_token}")

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

    logging.debug(f"code: {code}")
    user_token = register_by_code(code)
    if user_token is None:
        return "Failed to register by code."

    logging.debug(f"user_token: {user_token}")
    return user_token


app.register_blueprint(bp)
