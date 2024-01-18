from app import app
from flask import Blueprint, jsonify, request, session
from model.team import get_team_list_by_user_id, is_team_admin
from model.user import get_user_by_id
from utils.auth import authenticated

bp = Blueprint("user", __name__, url_prefix="/api")


@bp.route("/logout", methods=["GET"])
@authenticated
def logout():
    resp = jsonify(
        {
            "code": 0,
            "msg": "success",
        }
    )
    # clear session
    resp.set_cookie("session", "", expires=0)
    return resp


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
