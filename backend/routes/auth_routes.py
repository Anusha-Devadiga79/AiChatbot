from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from utils.db import get_db
from utils.auth_helpers import hash_password, verify_password, validate_email, validate_password
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    age = data.get("age")
    gender = data.get("gender", "").strip()

    # Validation
    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password are required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    valid_pw, pw_msg = validate_password(password)
    if not valid_pw:
        return jsonify({"error": pw_msg}), 400

    try:
        db = get_db()
        # Check existing user
        existing = db.table("users").select("user_id").eq("email", email).execute()
        if existing.data:
            return jsonify({"error": "Email already registered"}), 409

        hashed = hash_password(password)
        result = db.table("users").insert({
            "username": username,
            "email": email,
            "password": hashed,
            "age": age,
            "gender": gender,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        user = result.data[0]
        token = create_access_token(identity=str(user["user_id"]))
        return jsonify({"message": "Registration successful", "token": token,
                        "user": {"id": user["user_id"], "username": username, "email": email}}), 201
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        db = get_db()
        result = db.table("users").select("*").eq("email", email).execute()
        if not result.data:
            return jsonify({"error": "Invalid email or password"}), 401

        user = result.data[0]
        if not verify_password(password, user["password"]):
            return jsonify({"error": "Invalid email or password"}), 401

        token = create_access_token(identity=str(user["user_id"]))
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {"id": user["user_id"], "username": user["username"], "email": user["email"]}
        }), 200
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500
