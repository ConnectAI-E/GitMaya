import os

from app import app, session
from connectai.lark.oauth import Server as OauthServerBase
from connectai.lark.sdk import Bot, MarketBot
from connectai.lark.webhook import LarkServer as LarkServerBase

bot = Bot(
    app_id=os.environ.get("APP_ID"),
    app_secret=os.environ.get("APP_SECRET"),
    encrypt_key=os.environ.get("ENCRYPT_KEY"),
    verification_token=os.environ.get("VERIFICATION_TOKEN"),
)


class LarkServer(LarkServerBase):
    def get_bot(self, app_id):
        # TODO search in database and create Bot()
        return bot


class OauthServer(OauthServerBase):
    def get_bot(self, app_id):
        # TODO search in database and create Bot()
        return bot


hook = LarkServer(prefix="/api/feishu/hook")
oauth = OauthServer(prefix="/api/feishu/oauth")


@hook.on_bot_message(message_type="text", bot=bot)
def on_text_message(bot, message_id, content, *args, **kwargs):
    text = content["text"]
    print("reply_text", message_id, text)
    bot.reply_text(message_id, "reply: " + text)


@oauth.on_bot_event(event_type="oauth:user_info", bot=bot)
def on_oauth_user_info(bot, event_id, user_info, *args, **kwargs):
    # oauth user_info
    print("oauth", user_info)
    # TODO
    session["user_id"] = user_info["union_id"]
    session.permanent = True
    return user_info


app.register_blueprint(oauth.get_blueprint())
app.register_blueprint(hook.get_blueprint())
