from app import app
from flask import Blueprint, abort, jsonify, redirect, request, session
from model.team import (
    get_im_user_by_team_id,
    get_platform_info_by_team_id,
    get_team_by_id,
    get_team_list_by_user_id,
    get_team_member,
    is_team_admin,
    set_team_member,
)
from utils.auth import authenticated

bp = Blueprint("team", __name__, url_prefix="/api/team")


@bp.route("/", methods=["GET"])
@authenticated
def get_team_list():
    """
    get team list
    TODO
    """
    data, total = get_team_list_by_user_id(session["user_id"])
    return jsonify({"code": 0, "msg": "success", "data": data, "total": total})


@bp.route("/<team_id>", methods=["GET"])
@authenticated
def get_team_detail(team_id):
    team = get_team_by_id(team_id, session["user_id"])
    code_platform, im_platform = get_platform_info_by_team_id(team_id)
    return jsonify(
        {
            "code": 0,
            "msg": "success",
            "data": {
                "team": team,
                "code_platform": code_platform,
                "im_platform": im_platform,
            },
        }
    )


@bp.route("/<team_id>/member", methods=["GET"])
@authenticated
def get_team_member_by_team_id(team_id):
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=20, type=int)

    current_user = session["user_id"]
    data, total = get_team_member(team_id, current_user, page, size)
    return jsonify({"code": 0, "msg": "success", "data": data, "total": total})


@bp.route("/<team_id>/<platform>/user", methods=["GET"])
@authenticated
def get_im_user_by_team_id_and_platform(team_id, platform):
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=20, type=int)

    if platform not in ["lark"]:  # TODO lark/slack...
        return abort(400, "params error")

    current_user = session["user_id"]
    data, total = get_im_user_by_team_id(team_id, page, size)
    return jsonify(
        {
            "code": 0,
            "msg": "success",
            "data": [
                {
                    "value": i.user_id,
                    "label": i.name or i.email,
                    "email": i.email,
                    "avatar": i.avatar,
                }
                for i in data
            ],
            "total": total,
        }
    )


@bp.route("/<team_id>/member", methods=["POST"])
@authenticated
def save_team_member_by_team_id(team_id):
    code_user_id = request.json.get("code_user_id")
    im_user_id = request.json.get("im_user_id")
    if not code_user_id or not im_user_id:
        return abort(400, "params error")

    current_user = session["user_id"]
    is_admin = is_team_admin(team_id, current_user)
    if current_user != code_user_id and not is_admin:
        return abort(400, "permission error")

    set_team_member(team_id, code_user_id, im_user_id)
    return jsonify({"code": 0, "msg": "success"})


app.register_blueprint(bp)
