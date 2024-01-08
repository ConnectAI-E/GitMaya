import json
import logging
from functools import wraps

from connectai.lark.sdk import Bot
from model.schema import IMAction, IMApplication, IMEvent, ObjID, db


def get_bot_by_application_id(app_id):
    application = (
        db.session.query(IMApplication)
        .filter(
            IMApplication.app_id == app_id,
        )
        .first()
    )
    if application:
        return (
            Bot(
                app_id=application.app_id,
                app_secret=application.app_secret,
            ),
            application,
        )
    return None, None


def with_lark_storage(event_type="message"):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            1. 按默认的规则，args[-3:]  message_id/card_event_token, message_content/card_event, raw_message/raw_card_event
            2. 可以尝试读取message_id + message_content存 event数据库
            3. result = func(*args, **kwargs)
            4. result默认当成数组处理，然后，就可以把result的每一项存action数据表
            """
            event_id = None
            try:
                app_id, message_id, content, raw_message = args[-4:]
                application = (
                    db.session.query(IMApplication)
                    .filter(
                        IMApplication.app_id == app_id,
                    )
                    .first()
                )
                if "om_" in message_id and application:
                    event_id = ObjID.new_id()
                    db.session.add(
                        IMEvent(
                            id=event_id,
                            application_id=application.id,
                            event_id=message_id,
                            event_type=event_type,  # TODO 这里要不只存parser里面的command算了
                            content=json.dumps(content)[:128],
                            extra=raw_message,
                        )
                    )
                    db.session.commit()
            except Exception as e:
                logging.error(e)

            result = func(*args, **kwargs)

            try:
                # try save result
                if event_id:
                    results = result if isinstance(result, list) else [result]
                    for action_result in results:
                        message_id = (
                            action_result.get("data")
                            if isinstance(action_result, dict)
                            else ""
                        )
                        db.session.add(
                            IMAction(
                                id=ObjID.new_id(),
                                event_id=event_id,
                                message_id=message_id,
                                action_type=func.__name__,
                                content=json.dumps(action_result)[:128],
                                extra=action_result,
                            )
                        )
                    db.session.commit()
            except Exception as e:
                logging.error(e)
            return result

        return wrapper

    return decorate
