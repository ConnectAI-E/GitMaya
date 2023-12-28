import os
from connectai.lark.oauth import Server as OauthServer
from connectai.lark.sdk import Bot, MarketBot
from connectai.lark.webhook import LarkServer
from connectai.storage import ExpiredDictStorage


def get_app():
    hook = LarkServer()
    oauth = OauthServer()
    bot = Bot(
        app_id=os.environ.get("APP_ID"),
        app_secret=os.environ.get("APP_SECRET"),
        encrypt_key=os.environ.get("ENCRYPT_KEY"),
        verification_token=os.environ.get("VERIFICATION_TOKEN")
    )
    @hook.on_bot_message(message_type="text", bot=bot)
    def on_text_message(bot, message_id, content, *args, **kwargs):
        text = content["text"]
        print("reply_text", message_id, text)
        bot.reply_text(message_id, "reply: " + text)

    @oauth.on_bot_event(event_type="oauth:user_info", bot=bot)
    def on_oauth_user_info(bot, event_id, user_info, *args, **kwargs):
        # oauth user_info
        print("oauth", user_info)
        return user_info

    app = oauth.get_app()
    app.register_blueprint(hook.get_blueprint())
    return app

