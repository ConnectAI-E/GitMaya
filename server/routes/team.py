import logging

from app import app
from flask import Blueprint, abort, jsonify, redirect, request, session
from model.team import get_team_list_by_user_id
from utils.auth import authenticated

bp = Blueprint("team", __name__, url_prefix="/api/team")


@bp.route("/", methods=["GET"])
@authenticated
def get_team_list():
    """
    get team list
    TODO
    """
    data, total = get_team_list_by_user_id(session["user_id"])
    return jsonify({"code": 0, "msg": "success", "data": data, "total": total})


@app.route("/<name>")
@bp.route("/<team_id>", methods=["GET"])
@authenticated
def get_team_detail(team_id):
    data = get_team_by_id(team_id, session["user_id"])
    return jsonify({"code": 0, "msg": "success", "data": data})


app.register_blueprint(bp)
