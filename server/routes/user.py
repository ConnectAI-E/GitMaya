from app import app
from flask import Blueprint, Response, abort, jsonify, request, session
from model.team import (
    get_application_info_by_team_id,
    get_team_list_by_user_id,
    is_team_admin,
)
from model.user import get_user_by_id
from tasks.lark.base import get_bot_by_application_id, get_repo_by_repo_id
from utils.auth import authenticated
from utils.utils import download_file

bp = Blueprint("user", __name__, url_prefix="/api")


@bp.route("/logout", methods=["GET"])
@authenticated
def logout():
    # clear session
    session.clear()
    return jsonify(
        {
            "code": 0,
            "msg": "success",
        }
    )


@bp.route("/account", methods=["GET"])
@authenticated
def get_account():
    current_user = session["user_id"]
    user = get_user_by_id(current_user)
    teams, _ = get_team_list_by_user_id(current_user)
    current_team = session.get("team_id")
    if not current_team and len(teams) > 0:
        current_team = teams[0].id
    is_admin = is_team_admin(current_team, current_user) if current_team else False
    return jsonify(
        {
            "code": 0,
            "msg": "success",
            "data": {
                "user": user,
                "current_team": current_team,
                "is_team_admin": is_admin,
            },
        }
    )


@bp.route("/account", methods=["POST"])
@authenticated
def set_account():
    current_team = request.json.get("current_team")

    if current_team:
        session["team_id"] = current_team
        # 默认是会话级别的session，关闭浏览器直接就失效了
        session.permanent = True

    return jsonify({"code": 0, "msg": "success"})


@bp.route("/<team_id>/<message_id>/<repo_id>/image/<img_key>", methods=["GET"])
def get_image(team_id, message_id, repo_id, img_key):
    """
    1. 用 img_key 请求飞书接口下载 image
    2. 判断请求来源，如果是 GitHub 调用，则直接返回 image
    3. 用户调用 校验权限
    """

    def download_and_respond():
        _, im_application = get_application_info_by_team_id(team_id)
        bot, _ = get_bot_by_application_id(im_application.id)
        image_content = download_file(img_key, message_id, bot, "image")
        return Response(image_content, mimetype="image/png")

    # GitHub调用
    user_agent = request.headers.get("User-Agent")
    if user_agent and user_agent.startswith("github-camo"):
        return download_and_respond()

    # TODO 用户调用(弱需求, 通常来讲此接口不会被暴露), 需要进一步校验权限
    referer = request.headers.get("Referer")
    if not referer:
        # 公开仓库不校验
        repo = get_repo_by_repo_id(repo_id)
        is_private = repo.extra.get("private", False)
        app.logger.debug(f"is_private: {is_private}")

        # 私有仓库校验，先登录
        if is_private:
            return abort(403)

    return download_and_respond()


app.register_blueprint(bp)
