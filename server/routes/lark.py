import os

from app import app
from connectai.lark.oauth import Server as OauthServerBase
from connectai.lark.sdk import Bot, MarketBot
from connectai.lark.webhook import LarkServer as LarkServerBase
from flask import session
from model.lark import get_bot_by_app_id
from tasks.lark import get_contact_by_lark_application
from utils.lark.parser import GitMayaLarkParser


def get_bot(app_id):
    with app.app_context():
        application = get_bot_by_app_id(app_id)
        if application:
            return Bot(
                app_id=application.app_id,
                app_secret=application.app_secret,
                encrypt_key=application.extra.get("encrypt_key"),
                verification_token=application.extra.get("verification_token"),
            )


class LarkServer(LarkServerBase):
    def get_bot(self, app_id):
        return get_bot(app_id)


class OauthServer(OauthServerBase):
    def get_bot(self, app_id):
        return get_bot(app_id)


hook = LarkServer(prefix="/api/feishu/hook")
oauth = OauthServer(prefix="/api/feishu/oauth")
parser = GitMayaLarkParser()


@hook.on_bot_event(event_type="card:action")
def on_card_action(bot, token, data, *args, **kwargs):
    # TODO 将action中的按钮，或者选择的东西，重新组织成 command 继续走parser的逻辑
    if "action" in data and "command" in data["action"]["value"]:
        command = data["action"]["value"]["command"]
        suffix = data["action"]["value"].get("suffix")
        # 将选择的直接拼接到后面
        if suffix == "$option" and "option" in data:
            command = command + data["option"]
        try:
            parser.parse_args(
                command, bot.app_id, data["open_message_id"], data, *args, **kwargs
            )
        except Exception as e:
            app.logger.exception(e)
    else:
        app.logger.error("unkown card_action %r", (bot, token, data, *args))


@hook.on_bot_message(message_type="text")
def on_text_message(bot, message_id, content, *args, **kwargs):
    text = content["text"]
    # print("reply_text", message_id, text)
    # bot.reply_text(message_id, "reply: " + text)
    try:
        parser.parse_args(text, bot.app_id, message_id, content, *args, **kwargs)
    except Exception as e:
        app.logger.exception(e)


@oauth.on_bot_event(event_type="oauth:user_info")
def on_oauth_user_info(bot, event_id, user_info, *args, **kwargs):
    # oauth user_info
    print("oauth", user_info)
    # TODO save bind user
    session["user_id"] = user_info["union_id"]
    session.permanent = True
    # TODO ISV application
    if isinstance(bot, MarketBot):
        with app.app_context():
            task = get_contact_by_lark_application.delay(bot.app_id)
            app.logger.info("try get_contact_by_lark_application %r", bot.app_id)
    return user_info


app.register_blueprint(oauth.get_blueprint())
app.register_blueprint(hook.get_blueprint())
