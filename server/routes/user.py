from app import app
from flask import Blueprint, jsonify, request, session
from model.team import (
    get_application_info_by_team_id,
    get_team_list_by_user_id,
    is_team_admin,
)
from model.user import get_user_by_id
from tasks.lark.base import get_bot_by_application_id
from utils.auth import authenticated
from utils.utils import download_image

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


app.register_blueprint(bp)


@bp.route("/<team_id>/<message_id>/image/<img_key>", methods=["GET"])
@authenticated
def get_image(team_id, message_id, img_key):
    """
    1. 用 img_key 下载 image(cache)
    2. 这个链接需要用户登录信息
        1. 公开仓库，不校验
    3. 并且需要多加一层权限管理（只有这个team下面的人 ，才能查看这个图）
    4. 如果没有登录的时候，这个url返回一张403的图，点击的时候，告诉用户需要登录
        1. 如果是github上面查看的时候，通过 判断，展示图片
        2. 如果用户点击图片，直接浏览器打开
            1. 这个时候rederer是空的，跳转github　oauth登录
            2. 然后跳转回到这个图片。可以正常查看图片内容
            3. 这个时候如果刷新github的issue页面，应该是能正常查看图片的
    """
    # 必须要登录，才能查看图片，不然ddos分分钟打爆db
    _, im_application = get_application_info_by_team_id(team_id)
    bot, _ = get_bot_by_application_id(im_application.id)

    image_content = download_image(img_key, bot)
    return image_content
