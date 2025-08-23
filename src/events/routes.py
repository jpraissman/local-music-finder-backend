from flask import Blueprint, request, jsonify, Response, abort
import events.services.event_service as event_service

bp = Blueprint("events", __name__)


@bp.route("/", methods=["POST"])
def create_event():
    created_event = event_service.create_event(request.json)
    return jsonify(created_event.model_dump()), 201
