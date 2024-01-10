import logging
from email import message

from celery_app import app, celery
from model.schema import (
    BindUser,
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
from utils.lark.repo_manual import RepoManual
from utils.lark.repo_tip_failed import RepoTipFailed
from utils.lark.repo_tip_success import RepoTipSuccess

from .base import *


@celery.task()
def get_repo_url_by_chat_id(chat_id, *args, **kwargs):
    chat_group = get_repo_id_by_chat_group(chat_id)

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
def send_repo_failed_tip(content, app_id, message_id, *args, bot=None, **kwargs):
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
    return bot.reply(message_id, message).json()


@celery.task()
def send_repo_success_tip(content, app_id, message_id, *args, bot=None, **kwargs):
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
    message = RepoTipSuccess()(content=content)
    return bot.reply(message_id, message).json()


def _get_github_app(app_id, message_id, content, data):
    # 通过chat_group查repo id
    try:
        chat_id = data["event"]["message"]["chat_id"]
        openid = data["event"]["sender"]["sender_id"]["open_id"]
    except KeyError as e:
        logging.error(e)
        # card event
        chat_id = content["open_chat_id"]
        open_id = content["open_id"]

    logging.info(f"chat_id: {chat_id}")

    chat_group = get_repo_id_by_chat_group(chat_id)
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
        return send_repo_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, **kwargs
        )

    code_application = (
        db.session.query(CodeApplication)
        .filter(
            CodeApplication.id == repo.application_id,
        )
        .first()
    )
    if not code_application:
        return send_repo_failed_tip(
            "找不到对应的应用", app_id, message_id, content, data, *args, **kwargs
        )

    team = (
        db.session.query(Team)
        .filter(
            Team.id == code_application.team_id,
        )
        .first()
    )
    if not team:
        return send_repo_failed_tip(
            "找不到对应的项目", app_id, message_id, content, data, *args, **kwargs
        )

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
    )

    bot, _ = get_bot_by_application_id(app_id)
    return bot.reply(message_id, message).json()


@celery.task()
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
            "更新Repo失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response


@celery.task()
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
            "更新Repo失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response


@celery.task()
def change_repo_desc(desc, app_id, message_id, content, data, *args, **kwargs):
    """编辑 Repo"""
    bot, application = get_bot_by_application_id(app_id)
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == repo_id,
        )
        .first()
    )

    if repo:
        # TODO 修改 repo 描述, 调用github api，修改数据库和调用api要用事务
        repo.description = desc
        db.session.commit()

        message = RepoTipSuccess(f"已成功修改 {repo.description} 仓库描述为 {desc}")
        return bot.reply(message_id, message).json()

    return bot.reply(message_id, message).json()


@celery.task()
def change_repo_link(homepage, app_id, message_id, content, data, *args, **kwargs):
    """修改homepage link"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.update_repo(
        team.name,
        repo.name,
        homepage=homepage,
    )
    if "id" not in response:
        return send_repo_failed_tip(
            "更新Repo失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response


@celery.task()
def change_repo_label(label, app_id, message_id, content, data, *args, **kwargs):
    """修改homepage topic"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.replace_topics(
        team.name,
        repo.name,
        label,
    )
    if "id" not in response:
        return send_repo_failed_tip(
            "更新Repo失败", app_id, message_id, content, data, *args, **kwargs
        )
    return response


@celery.task()
def change_repo_archive(archived, app_id, message_id, content, data, *args, **kwargs):
    """修改homepage archive status"""
    github_app, team, repo = _get_github_app(app_id, message_id, content, data)

    response = github_app.update_repo(
        team.name,
        repo.name,
        archived=archived,
    )
    if "id" not in response:
        return send_repo_failed_tip(
            "更新Repo失败", app_id, message_id, content, data, *args, **kwargs
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

        message = RepoInfo(
            repo_url=f"https://github.com/{team.name}/{repo.name}",
            repo_name=repo.name,
            repo_description=repo.description,
            repo_topic=repo.extra.get("topic", []),
            open_issues_count=repo.extra.get("open_issues_count", 0),
            stargazers_count=repo.extra.get("stargazers_count", 0),
            forks_count=repo.extra.get("forks_count", 0),
            visibility="私有仓库" if repo.extra.get("private") else "公开仓库",
            updated=repo.extra.get("updated_at", ""),
        )

        return bot.update(message_id=repo.message_id, content=message).json()
    else:
        app.logger.error(f"Repo {repo_id} not found")
        return None
