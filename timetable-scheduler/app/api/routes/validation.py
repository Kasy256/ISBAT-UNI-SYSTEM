"""Validation service endpoints."""

from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("validation", __name__, url_prefix="/validation")


def register(app, auth_backend):
    require_admin = auth_backend.require_roles("admin")

    @bp.post("/run")
    @require_admin
    def run_validation():
        payload = request.get_json(force=True)
        result = current_app.validation_service.run(payload)
        return jsonify(result)

    app.register_blueprint(bp)
