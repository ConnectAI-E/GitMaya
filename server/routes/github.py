import json
import os

from app import app
from flask import Blueprint, jsonify, make_response, redirect, request, session
from model.team import create_code_application, create_team
from tasks.github import pull_github_repo
from tasks.github.issue import on_issue, on_issue_comment
from tasks.github.organization import on_organization
from tasks.github.pull_request import on_pull_request
from tasks.github.push import on_push
from tasks.github.repo import on_fork, on_repository, on_star
from utils.auth import authenticated
from utils.github.application import verify_github_signature
from utils.github.bot import BaseGitHubApp
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
            f"https://github.com/apps/{(os.environ.get('GITHUB_APP_NAME')).replace(' ', '-')}/installations/new"
        )

    github_app = BaseGitHubApp(installation_id)

    try:
        app_info = github_app.get_installation_info()

        if app_info is None:
            app.logger.error("Failed to get installation info.")
            raise Exception("Failed to get installation info.")

        # 判断安装者的身份是用户还是组织
        app_type = app_info["account"]["type"]
        if app_type == "User":
            app.logger.error("User is not allowed to install.")
            raise Exception("User is not allowed to install.")

        team = create_team(app_info, contact_id=session.get("contact_id"))
        code_application = create_code_application(team.id, installation_id)

        # if app_info == "organization":
        # 在后台任务中拉取仓库
        task = pull_github_repo.delay(
            org_name=app_info["account"]["login"],
            installation_id=installation_id,
            application_id=code_application.id,
            team_id=team.id,
        )

        message = dict(
            status=True,
            event="installation",
            data=app_info,
            team_id=team.id,
            task_id=task.id,
            app_type=app_type,
        )

    except Exception as e:
        # 返回错误信息
        app.logger.error(e)
        app_info = str(e)
        message = dict(
            status=False,
            event="installation",
            data=app_info,
            team_id=None,
            task_id=None,
            app_type=app_type,
        )

    return make_response(
        """
<script>
try {
  window.opener.postMessage("""
        + json.dumps(message)
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


@bp.route("/oauth", methods=["GET"])
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
    # if user_id is None:
    #     return jsonify({"message": "Failed to register."}), 500

    # 保存用户注册状态
    if user_id:
        session["user_id"] = user_id
        # 默认是会话级别的session，关闭浏览器直接就失效了
        session.permanent = True

    return make_response(
        """
<script>
try {
  window.opener.postMessage("""
        + json.dumps(dict(event="oauth", data={"user_id": user_id}))
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


@bp.route("/hook", methods=["POST"])
@verify_github_signature(os.environ.get("GITHUB_WEBHOOK_SECRET"))
def github_hook():
    """Receive GitHub webhook."""

    x_github_event = request.headers.get("x-github-event", None).lower()

    app.logger.info(x_github_event)

    match x_github_event:
        case "repository":
            task = on_repository.delay(request.json)
            return jsonify({"code": 0, "message": "ok", "task_id": task.id})
        case "issues":
            task = on_issue.delay(request.json)
            return jsonify({"code": 0, "message": "ok", "task_id": task.id})
        case "issue_comment":
            task = on_issue_comment.delay(request.json)
            return jsonify({"code": 0, "message": "ok", "task_id": task.id})
        case "pull_request":
            task = on_pull_request.delay(request.json)
            return jsonify({"code": 0, "message": "ok", "task_id": task.id})
        case "organization":
            task = on_organization.delay(request.json)
            return jsonify({"code": 0, "message": "ok", "task_id": task.id})
        case "push":
            task = on_push.delay(request.json)
            return jsonify({"code": 0, "message": "ok", "task_id": task.id})
        case "star":
            task = on_star.delay(request.json)
            return jsonify({"code": 0, "message": "ok", "task_id": task.id})
        case "fork":
            task = on_fork.delay(request.json)
            return jsonify({"code": 0, "message": "ok", "task_id": task.id})
        case _:
            app.logger.info(f"Unhandled GitHub webhook event: {x_github_event}")
            return jsonify({"code": -1, "message": "Unhandled GitHub webhook event."})

    return jsonify({"code": 0, "message": "ok"})


app.register_blueprint(bp)
