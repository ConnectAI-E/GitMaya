import logging

from app import app
from flask import Blueprint, abort, jsonify, redirect, request
from utils.auth import authenticated

bp = Blueprint("team", __name__, url_prefix="/api/team")


@bp.route("/", methods=["GET"])
@authenticated
def get_team_list():
    """
    get team list
    TODO
    """
    return jsonify({"code": 0, "msg": "success", "data": [], "total": 0})


app.register_blueprint(bp)
