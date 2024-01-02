import logging
import os

from app import app
from connectai.lark.oauth import Server as OauthServerBase
from connectai.lark.sdk import Bot, MarketBot
from connectai.lark.webhook import LarkServer as LarkServerBase
from flask import session
from model.lark import get_bot_by_app_id


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


@hook.on_bot_message(message_type="text")
def on_text_message(bot, message_id, content, *args, **kwargs):
    text = content["text"]
    print("reply_text", message_id, text)
    bot.reply_text(message_id, "reply: " + text)


@oauth.on_bot_event(event_type="oauth:user_info")
def on_oauth_user_info(bot, event_id, user_info, *args, **kwargs):
    # oauth user_info
    print("oauth", user_info)
    # TODO save bind user
    session["user_id"] = user_info["union_id"]
    session.permanent = True
    return user_info


app.register_blueprint(oauth.get_blueprint())
app.register_blueprint(hook.get_blueprint())
