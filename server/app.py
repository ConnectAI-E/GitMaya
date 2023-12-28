import os

from flask import Flask, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
db = SQLAlchemy(app, engine_options={"isolation_level": "AUTOCOMMIT"})
CORS(
    app, allow_headers=["Authorization", "X-Requested-With"], supports_credentials=True
)

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
