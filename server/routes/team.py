import json
import os

from app import app
from flask import Blueprint, abort, jsonify, make_response, redirect, request, session
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
    save_team_contact,
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


@bp.route("/<team_id>/<platform>/app", methods=["GET"])
@authenticated
def install_im_application_to_team_by_get_method(team_id, platform):
    # install lark app
    if platform not in ["lark"]:  # TODO lark/slack...
        return abort(400, "params error")

    redirect_uri = request.base_url
    if request.headers.get("X-Forwarded-Proto") == "https":
        redirect_uri = redirect_uri.replace("http://", "https://")
    app_id = request.args.get("app_id", "")
    name = request.args.get("name", "")
    if app_id:
        # 2. deploy server重定向过来：带app_id以及app_secret，保存，并带上redirect_uri重定向到deploy server
        app_secret = request.args.get("app_secret")
        if app_secret:
            encrypt_key = request.args.get("encrypt_key", "")
            verification_token = request.args.get("verification_token", "")
            if not app_id or not app_secret:
                return abort(400, "params error")

            result = save_im_application(
                team_id, platform, app_id, app_secret, encrypt_key, verification_token
            )
            app.logger.info("result %r", result)
            events = [
                "20",
                "im.message.message_read_v1",
                "im.message.reaction.created_v1",
                "im.message.reaction.deleted_v1",
                "im.message.recalled_v1",
                "im.message.receive_v1",
            ]
            scope_ids = [
                "8002",
                "100032",
                "6081",
                "14",
                "1",
                "21001",
                "20001",
                "20011",
                "3001",
                "20012",
                "20010",
                "3000",
                "20008",
                "1000",
                "20009",
            ]
            hook_url = f"{os.environ.get('DOMAIN')}/api/feishu/hook/{app_id}"
            return redirect(
                f"{os.environ.get('LARK_DEPLOY_SERVER')}/publish?redirect_uri={redirect_uri}&app_id={app_id}&events={','.join(events)}&encrypt_key={encrypt_key}&verification_token={verification_token}&scopes={','.join(scope_ids)}&hook_url={hook_url}"
            )
        else:
            # 3. deploy server只带app_id重定向过来：说明已经安装成功，这个时候通知前端成功
            if not name:
                return make_response(
                    """
<script>
try {
  (window.opener || window.parent).postMessage("""
                    + json.dumps(dict(event="installation", app_id=app_id, data=app_id))
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

    # 1. 前端重定向过来：重定向到deploy server
    desc = request.args.get("desc", "")
    avatar = request.args.get(
        "avatar",
        "https://s1-imfile.feishucdn.com/static-resource/v1/v3_0074_5ae2ba69-5729-445e-afe7-4a19d1fb0a2g",
    )
    if not name and not desc:
        return abort(400, "params error")
    # 如果传app_id就是更新app
    return redirect(
        f"{os.environ.get('LARK_DEPLOY_SERVER')}?redirect_uri={redirect_uri}&app_id={app_id}&name={name}&desc={desc}&avatar={avatar}"
    )


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


@bp.route("/contact", methods=["POST"])
@authenticated
def _save_team_contact():
    current_user = session["user_id"]
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    email = request.json.get("email")
    role = request.json.get("role")
    newsletter = request.json.get("newsletter")
    contact_id = save_team_contact(
        current_user, first_name, last_name, email, role, newsletter
    )
    session["contact_id"] = contact_id
    session.permanent = True
    return jsonify({"code": 0, "msg": "success"})


app.register_blueprint(bp)
