import json
import logging

from celery_app import app, celery
from connectai.lark.sdk import Bot
from model.schema import ChatGroup, Repo, Team, db
from sqlalchemy.orm import aliased
from utils.lark.chat_manual import ChatManual
from utils.lark.chat_tip_failed import ChatTipFailed
from utils.lark.issue_card import IssueCard

from .manage import get_bot_by_application_id


@celery.task()
def send_chat_failed_tip(content, app_id, message_id, *args, bot=None, **kwargs):
    """send new repo card message to user.

    Args:
        app_id: IMApplication.app_id.
        message_id: lark message id.
        content: error message
    """
    if not bot:
        bot, _ = get_bot_by_application_id(app_id)
    message = ChatTipFailed(content=content)
    return bot.reply(message_id, message).json()


@celery.task()
def send_chat_manual(app_id, message_id, content, data, *args, **kwargs):
    chat_id = data["event"]["message"]["chat_id"]
    chat_group = (
        db.session.query(ChatGroup)
        .filter(
            ChatGroup.chat_id == chat_id,
            ChatGroup.status == 0,
        )
        .first()
    )
    if not chat_group:
        return send_chat_failed_tip(
            "找不到项目群", app_id, message_id, content, data, *args, **kwargs
        )
    repo = (
        db.session.query(Repo)
        .filter(
            Repo.id == chat_group.repo_id,
            Repo.status == 0,
        )
        .first()
    )
    if not repo:
        return send_chat_failed_tip(
            "找不到项目群", app_id, message_id, content, data, *args, **kwargs
        )
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_manage_fail_message(
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
        return send_manage_fail_message(
            "找不到对应的项目", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    message = ChatManual(
        repo_url=f"https://github.com/{team.name}/{repo.name}",
        repo_name=repo.name,
        actions=[],  # TODO 获取actions
    )
    return bot.reply(message_id, message).json()


@celery.task()
def create_issue(
    title, users, labels, app_id, message_id, content, data, *args, **kwargs
):
    bot, application = get_bot_by_application_id(app_id)
    if not application:
        return send_manage_fail_message(
            "找不到对应的应用", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )
    if not title:
        # 如果title是空的，尝试从parent_message拿到内容
        parent_id = data["event"]["message"].get("parent_id")
        if parent_id:
            parent_message_url = f"{bot.host}/open-apis/im/v1/messages/{parent_id}"
            result = bot.get(parent_message_url).json()
            if len(result["data"].get("items", [])) > 0:
                parent_message = result["data"]["items"][0]
                title = json.loads(parent_message["body"]["content"]).get("text")
    if not title:
        return send_manage_fail_message(
            "issue 标题为空", app_id, message_id, content, data, *args, bot=bot, **kwargs
        )

    # TODO 调用github api生成issue
    # create_github_issue(title, users, labels)
    message = IssueCard(
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        id=16,
        title="优化 OpenAI 默认返回的表格在飞书对话中的呈现",
        description="💬  <font color='black'>**主要内容**</font>\n功能改善建议 🚀\n优化 OpenAI 默认返回的表格在飞书对话中的呈现。\n\n## 您的建议是什么？ 🤔\n\n当前问题1：当要求 OpenAI 使用表格对内容进行格式化返回时，默认会返回 Markdown 格式的文本形式，在飞书对话中显示会很混乱，特别是在手机上查看时。\n\n当前问题2：飞书对话默认不支持 Markdown 语法表格的可视化。\n\n功能预期：返回对话消息如果识别为包含表格内容，支持将内容输出至飞书多维表格，并在对话中返回相应链接。",
        status="待完成",
        assignees=users,
        tags=labels,
        updated="2022年12月23日 16:32",
    )
    # return bot.reply(message_id, message).json()
    # TODO 回复或者直接发卡片
    chat_id = data["event"]["message"]["chat_id"]
    return bot.send(chat_id, message, receive_id_type="chat_id").json()
