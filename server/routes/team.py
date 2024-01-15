from app import app
from flask import Blueprint, abort, jsonify, redirect, request, session
from model.team import (
    create_repo_chat_group_by_repo_id,
    get_application_info_by_team_id,
    get_im_user_by_team_id,
    get_team_by_id,
    get_team_list_by_user_id,
    get_team_member,
    get_team_repo,
    is_team_admin,
    save_im_application,
    set_team_member,
)
from tasks import get_contact_by_lark_application, get_status_by_id, pull_github_members
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
    code_application, im_application = get_application_info_by_team_id(team_id)
    return jsonify(
        {
            "code": 0,
            "msg": "success",
            "data": {
                "team": team,
                "code_application": code_application,
                "im_application": im_application,
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
                    "value": i.id,
                    "label": i.name or i.email,
                    "email": i.email,
                    "avatar": i.avatar,
                }
                for i in data
            ],
            "total": total,
        }
    )


@bp.route("/<team_id>/member", methods=["PUT"])
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


@bp.route("/<team_id>/member", methods=["POST"])
@authenticated
def refresh_team_member_by_team_id(team_id):
    code_application, _ = get_application_info_by_team_id(team_id)
    if not code_application:
        app.logger.error("code_application not found")
        return abort(400, "params error")

    team = get_team_by_id(team_id, session["user_id"])

    task = pull_github_members.delay(
        code_application.installation_id,
        team.name,
        team_id,
        code_application.id,
    )

    return jsonify({"code": 0, "msg": "success", "data": {"task_id": task.id}})


@bp.route("/<team_id>/<platform>/app", methods=["POST"])
@authenticated
def install_im_application_to_team(team_id, platform):
    # install lark app
    if platform not in ["lark"]:  # TODO lark/slack...
        return abort(400, "params error")

    app_id = request.json.get("app_id")
    app_secret = request.json.get("app_secret")
    encrypt_key = request.json.get("encrypt_key")
    verification_token = request.json.get("verification_token")
    if not app_id or not app_secret:
        return abort(400, "params error")

    result = save_im_application(
        team_id, platform, app_id, app_secret, encrypt_key, verification_token
    )
    app.logger.info("result %r", result)
    return jsonify({"code": 0, "msg": "success"})


@bp.route("/<team_id>/<platform>/user", methods=["POST"])
@authenticated
def refresh_im_user_by_team_id_and_platform(team_id, platform):
    # trigger task
    if platform not in ["lark"]:  # TODO lark/slack...
        return abort(400, "params error")
    _, im_application = get_application_info_by_team_id(team_id)
    task = get_contact_by_lark_application.delay(im_application.id)
    return jsonify({"code": 0, "msg": "success", "data": {"task_id": task.id}})


@bp.route("/<team_id>/task/<task_id>", methods=["GET"])
@authenticated
def get_task_result_by_id(team_id, task_id):
    # get task result
    task = get_status_by_id(task_id)
    return jsonify(
        {
            "code": 0,
            "msg": "success",
            "data": {
                "task_id": task.id,
                "status": task.status,
                "result": task.result
                if isinstance(task.result, list)
                else str(task.result),
            },
        }
    )


@bp.route("/<team_id>/repo", methods=["GET"])
@authenticated
def get_team_repo_by_team_id(team_id):
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=20, type=int)

    current_user = session["user_id"]
    data, total = get_team_repo(team_id, current_user, page, size)
    return jsonify({"code": 0, "msg": "success", "data": data, "total": total})


@bp.route("/<team_id>/repo/<repo_id>/chat", methods=["POST"])
@authenticated
def create_repo_chat_group(team_id, repo_id):
    name = request.json.get("name")
    current_user = session["user_id"]
    create_repo_chat_group_by_repo_id(current_user, team_id, repo_id, name)
    return jsonify({"code": 0, "msg": "success"})


app.register_blueprint(bp)
