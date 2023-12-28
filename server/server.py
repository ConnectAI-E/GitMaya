import os
from dotenv import find_dotenv, load_dotenv
from app import get_app

load_dotenv(find_dotenv())
app = get_app()


if __name__ == "__main__":
    # gunicorn -w 1 -b :8888 "server:app"
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=os.environ.get("PORT", 8888))

