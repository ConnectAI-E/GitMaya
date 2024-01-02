import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_prefixed_env()
app.secret_key = os.environ.get("SECRET_KEY")
db = SQLAlchemy(app, engine_options={"isolation_level": "AUTOCOMMIT"})
CORS(
    app, allow_headers=["Authorization", "X-Requested-With"], supports_credentials=True
)


@app.errorhandler(404)
def custom404(error):
    response = jsonify({"code": -1, "msg": error.description})
    response.status_code = 404
    return response


gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
