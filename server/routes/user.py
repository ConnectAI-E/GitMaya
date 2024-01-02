import logging

from app import app
from flask import Blueprint, jsonify, session
from model.team import get_team_list_by_user_id, is_team_admin
from model.user import get_user_by_id
from utils.auth import authenticated

bp = Blueprint("user", __name__, url_prefix="/api")


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


app.register_blueprint(bp)
