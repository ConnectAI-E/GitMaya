from functools import wraps

from flask import abort, session


def authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return abort(401)
        return func(*args, **kwargs)

    return wrapper
