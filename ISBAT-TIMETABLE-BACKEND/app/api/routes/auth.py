"""Authentication endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ...middleware.auth import AuthError
from ...models.user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")
USERS: dict[str, User] = {}


def register(app, auth_backend) -> None:
    USERS.setdefault("admin", User.create("admin", "admin123", ["admin"]))

    @bp.post("/login")
    def login():
        data = request.get_json(force=True)
        user = USERS.get(data.get("username"))
        if not user or not user.verify_password(data.get("password", "")):
            raise AuthError("Invalid credentials")
        token = auth_backend.encode(user.username, user.roles)
        return jsonify({"access_token": token, "roles": user.roles})

    @bp.post("/register")
    def register_user():
        data = request.get_json(force=True)
        username = data["username"]
        if username in USERS:
            return jsonify({"error": "User exists"}), 400
        USERS[username] = User.create(username, data["password"], data.get("roles", ["viewer"]))
        return jsonify({"username": username, "roles": USERS[username].roles}), 201

    app.register_blueprint(bp)
