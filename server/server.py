import os

import env
import routes
from app import app

if __name__ == "__main__":
    # gunicorn -w 1 -b :8888 "server:app"
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=os.environ.get("PORT", 8888))
