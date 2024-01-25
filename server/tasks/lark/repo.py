import logging
from email import message

from celery_app import app, celery
from model.schema import (
    CodeApplication,
    CodeUser,
    IMApplication,
    IMUser,
    Repo,
    Team,
    TeamMember,
    db,
)
from utils.github.repo import GitHubAppRepo
from utils.lark.repo_info import RepoInfo
from utils.lark.repo_manual import RepoManual, RepoView
from utils.lark.repo_tip_failed import RepoTipFailed
from utils.lark.repo_tip_success import RepoTipSuccess

from .base import *


@celery.task()
def get_repo_url_by_chat_id(chat_id, *args, **kwargs):
    chat_group = get_chat_group_by_chat_id(chat_id)

    repo_name = get_repo_name_by_repo_id(chat_group.repo_id)
    team = (
        db.session.query(Team)
        .filter(
            Team.id == chat_group.team_id,
            Team.status == 0,
        )
        .first()
    )
    return f"https://github.com/{team.name}/{repo_name}"


@celery.task()
def get_repo_name_by_chat_id(chat_id, *args, **kwargs):
    chat_group = get_chat_group_by_chat_id(chat_id)
    return get_repo_name_by_repo_id(chat_group.repo_id)


@celery.task()
def send_repo_failed_tip(
    content, app_id, message_id, data, raw_message, *args, bot=None, **kwargs
):
    """send a new repo failed tip to user.
    Args:
        content (str): The error message to be sent.
        app_id (str): The ID of the IM application.
        message_id (str): The ID of the Lark message.
        bot (Bot, optional): The bot instance. Defaults to None.
    Returns:
        dict: The JSON response from the bot's reply method.
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = RepoTipFailed(content=content)
    open_id = raw_message["event"]["sender"]["sender_id"].get("open_id", None)
    return bot.reply(message_id, message).json()


@celery.task()
def send_repo_success_tip(
    content, app_id, message_id, data, raw_message, *args, bot=None, **kwargs
):
    """send new repo success tip to user.

    Args:
        content (str): The success message to be sent.
        app_id (str): The ID of the IMApplication.
        message_id (str): The ID of the lark message.
        bot (Bot, optional): The bot instance. Defaults to None.

    Returns:
        dict: The JSON response from the bot's reply method.
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = RepoTipSuccess(content=content)
    open_id = raw_message["event"]["sender"]["sender_id"].get("open_id", None)
    return bot.reply(message_id, message).json()


def _get_github_app(app_id, message_id, content, data):
    # 通过chat_group查repo id
    chat_id = data["event"]["message"]["chat_id"]
    openid = data["event"]["sender"]["sender_id"]["open_id"]

    logging.info(f"chat_id: {chat_id}")

    chat_group = get_chat_group_by_chat_id(chat_id)
    logging.info(f"chat_group: {chat_group}")

    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == chat_group.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    logging.info(f"repo: {repo}")
    if not repo:
        return send_repo_failed_tip("找不到对应的项目", app_id, message_id, content, data)

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.id == repo.application_id,
        )
        .first()
    )

    if not code_application:
        return send_repo_failed_tip("找不到对应的应用", app_id, message_id, content, data)

    team = (
        db.session.query(Team)
        .filter(
            Team.id == code_application.team_id,
        )
        .first()
    )
    if not team:
        return send_repo_failed_tip("找不到对应的项目", app_id, message_id, content, data)

    code_user_id = (
        db.session.query(CodeUser.user_id)
        .join(
            TeamMember,
            TeamMember.code_user_id == CodeUser.id,
        )
        .join(
            IMUser,
            IMUser.id == TeamMember.im_user_id,
        )
        .filter(
            IMUser.openid == openid,
            TeamMember.team_id == team.id,
        )
        .limit(1)
        .scalar()
    )

    github_app = GitHubAppRepo(code_application.installation_id, user_id=code_user_id)
    return github_app, team, repo


@celery.task()
def send_repo_manual(app_id, message_id, content, data, *args, **kwargs):
    """
    Send repository manual to a chat group.

    Args:
        app_id (int): The ID of the application.
        message_id (int): The ID of the message.
        data (dict): The data containing the event message and chat ID.

    Returns:
        dict: The JSON response from the bot.

    """
    _, team, repo = _get_github_app(app_id, message_id, content, data)

    message = RepoManual(
        repo_url=f"https://github.com/{team.name}/{repo.name}",
        repo_name=repo.name,
        visibility=repo.extra.get("visibility", "public"),
        archived=True if repo.extra.get("archived") else False,
    )

    bot, _ = get_bot_by_application_id(app_id)
    return bot.reply(message_id, message).json()


def send_repo_url_message(
    app_id, message_id, content, data, *args, typ="view", **kwargs
):
    root_id = data["event"]["message"]["root_id"]
    repo, _, _ = get_git_object_by_message_id(root_id)
    if not repo:
        return send_repo_failed_tip(
            "找不到Repo", app_id, message_id, content, data, *args, **kwargs
        )
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_repo_failed_tip(
            "找不到对应的应用", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == application.team_id,
        )
        .first()
    )
    if not team:
        return send_repo_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    repo_url = f"https://github.com/{team.name}/{repo.name}"
    if "view" == typ:
        message = RepoView(repo_url=repo_url)
    elif "insight" == typ:
        message = RepoView(repo_url=f"{repo_url}/pulse")
    return bot.reply(message_id, message).json()


@celery.task()
def send_repo_view_message(app_id, message_id, content, data, *args, **kwargs):
    return send_repo_url_message(
        app_id, message_id, content, data, *args, typ="view", **kwargs
    )


@celery.task()
def send_repo_insight_message(app_id, message_id, content, data, *args, **kwargs):
    return send_repo_url_message(
        app_id, message_id, content, data, *args, typ="insight", **kwargs
    )


@celery.task()
@with_authenticated_github()
def change_repo_visit(visibility, app_id, message_id, content, data, *args, **kwargs):
    """修改 Repo 访问权限"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.update_repo(
        team.name,
        repo.name,
        visibility=visibility,
    )
    if "id" not in response:
        return send_repo_failed_tip(
            f"修改 {repo.name} 仓库访问权限失败",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )
    vis = "公开仓库" if visibility else "私有仓库"
    send_repo_success_tip(
        f"修改 {repo.name} 仓库访问权限为 {vis}",
        app_id,
        message_id,
        content,
        data,
        *args,
        **kwargs,
    )

    return response


@celery.task()
@with_authenticated_github()
def change_repo_name(name, app_id, message_id, content, data, *args, **kwargs):
    """修改 Repo 标题"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.update_repo(
        team.name,
        repo.name,
        name=name,
    )
    if "id" not in response:
        return send_repo_failed_tip(
            f"修改 {repo.name} 仓库标题失败", app_id, message_id, content, data, *args, **kwargs
        )

    send_repo_success_tip(
        f"修改 {repo.name} 仓库标题为 {name}",
        app_id,
        message_id,
        content,
        data,
        *args,
        **kwargs,
    )

    return response


@celery.task()
@with_authenticated_github()
def change_repo_desc(description, app_id, message_id, content, data, *args, **kwargs):
    """修改 Repo 描述"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.update_repo(
        team.name,
        repo.name,
        description=description,
    )
    if "id" not in response:
        return send_repo_failed_tip(
            f"修改 {repo.name} 仓库描述失败", app_id, message_id, content, data, *args, **kwargs
        )

    send_repo_success_tip(
        f"修改 {repo.name} 仓库描述为 {description}",
        app_id,
        message_id,
        content,
        data,
        *args,
        **kwargs,
    )

    return response


@celery.task()
@with_authenticated_github()
def change_repo_link(homepage, app_id, message_id, content, data, *args, **kwargs):
    """修改 homepage 链接"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.update_repo(
        team.name,
        repo.name,
        homepage=homepage,
    )
    if "id" not in response:
        return send_repo_failed_tip(
            f"修改 {repo.name} 仓库 homepage 链接失败",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )

    send_repo_success_tip(
        f"修改 {repo.name} 仓库 homepage 为 {homepage}",
        app_id,
        message_id,
        content,
        data,
        *args,
        **kwargs,
    )

    return response


@celery.task()
@with_authenticated_github()
def change_repo_label(label, app_id, message_id, content, data, *args, **kwargs):
    """修改 Repo 标签"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.replace_topics(
        team.name,
        repo.name,
        label,
    )
    if "names" not in response:
        return send_repo_failed_tip(
            f"修改 {repo.name} 仓库标签失败", app_id, message_id, content, data, *args, **kwargs
        )
    # label是个数组，把每个元素用逗号拼接起来变成labels
    labels = ",".join(label)
    send_repo_success_tip(
        f"修改 {repo.name} 仓库标签为 {label}",
        app_id,
        message_id,
        content,
        data,
        *args,
        **kwargs,
    )

    return response


@celery.task()
@with_authenticated_github()
def change_repo_archive(archived, app_id, message_id, content, data, *args, **kwargs):
    """修改 Repo archive 状态"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.update_repo(
        team.name,
        repo.name,
        archived=archived,
    )
    if "id" not in response:
        return send_repo_failed_tip(
            f"修改 {repo.name} 仓库 archive 状态失败",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )

    archived = "已归档" if archived else "未归档"
    send_repo_success_tip(
        f"修改 {repo.name} 仓库状态为 {archived}", app_id, message_id, content, data
    )

    message = RepoManual(
        repo_url=f"https://github.com/{team.name}/{repo.name}",
        repo_name=repo.name,
        visibility=repo.extra.get("visibility", "public"),
        archived=archived,
    )
    # 卡片有一个archive按钮，可以更新状态
    # TODO 这里延迟处理才能更新状态?
    bot, _ = get_bot_by_application_id(app_id)
    bot.update(message_id=message_id, content=message)
    return response


@celery.task()
@with_authenticated_github()
def change_repo_collaborator(
    permission, openid, app_id, message_id, content, data, *args, **kwargs
):
    """修改 Repo collaborator"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    # 从openid找到用户
    username = (
        db.session.query(CodeUser.name)
        .join(TeamMember, TeamMember.code_user_id == CodeUser.id)
        .join(
            IMUser,
            IMUser.id == TeamMember.im_user_id,
        )
        .filter(
            TeamMember.team_id == team.id,
            IMUser.openid == openid,
            CodeUser.platform == "github",
        )
        .limit(1)
        .scalar()
    )
    if not username:
        return send_repo_failed_tip(
            f"修改 {repo.name} 仓库 collaborator 失败: 找不到绑定人员",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )
    response = github_app.add_repo_collaborator(
        team.name,
        repo.name,
        username,
        permission,
    )
    if "status" not in response or response["status"] != "success":
        return send_repo_failed_tip(
            f"修改 {repo.name} 仓库 collaborator 失败: 添加人员失败",
            app_id,
            message_id,
            content,
            data,
            *args,
            **kwargs,
        )

    send_repo_success_tip(
        f"修改 {repo.name} 仓库 collaborator 成功",
        app_id,
        message_id,
        content,
        data,
        *args,
        **kwargs,
    )

    return response


@celery.task()
def update_repo_info(repo_id: str) -> dict | None:
    """Update the repo information.

    Args:
        repo_id (str): The ID of the repo.
        message_id (str): The ID of the message.

    Returns:
        dict: The JSON response from the bot's reply method.
    """

    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.id == repo.application_id,
        )
        .first()
    )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == code_application.team_id,
        )
        .first()
    )

    im_application = (
        db.session.query(IMApplication)
        .filter(
            IMApplication.team_id == team.id,
        )
        .first()
    )

    if repo:
        bot, _ = get_bot_by_application_id(im_application.app_id)

        repo_url = f"https://github.com/{team.name}/{repo.name}"
        message = RepoInfo(
            repo_url=repo_url,
            repo_name=repo.name,
            repo_description=repo.description,
            repo_topic=repo.extra.get("topics", []),
            homepage=repo.extra.get("homepage", None),
            open_issues_count=repo.extra.get("open_issues_count", 0),
            stargazers_count=repo.extra.get("stargazers_count", 0),
            forks_count=repo.extra.get("forks_count", 0),
            visibility="私有仓库" if repo.extra.get("private") else "公开仓库",
            archived=repo.extra.get("archived", False),
            updated=repo.extra.get("updated_at", ""),
        )

        return bot.update(message_id=repo.message_id, content=message).json()
    else:
        app.logger.error(f"update_repo_info: Repo {repo_id} not found")
        return None
