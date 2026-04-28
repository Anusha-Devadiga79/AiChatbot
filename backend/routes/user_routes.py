from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db
from utils.auth_helpers import validate_email, allowed_file, get_file_type
from werkzeug.utils import secure_filename
import os

user_bp = Blueprint("user", __name__)

@user_bp.route("/get", methods=["GET"])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    try:
        db = get_db()
        result = db.table("users").select("user_id, username, email, age, gender, profile_photo, created_at").eq("user_id", user_id).execute()
        if not result.data:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user": result.data[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/edit", methods=["PUT"])
@jwt_required()
def edit_user():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    allowed_fields = ["username", "age", "gender"]
    updates = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

    if "email" in data:
        if not validate_email(data["email"]):
            return jsonify({"error": "Invalid email format"}), 400
        updates["email"] = data["email"]

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    try:
        db = get_db()
        result = db.table("users").update(updates).eq("user_id", user_id).execute()
        return jsonify({"message": "Profile updated successfully", "user": result.data[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/upload-photo", methods=["POST"])
@jwt_required()
def upload_photo():
    user_id = get_jwt_identity()
    if "photo" not in request.files:
        return jsonify({"error": "No photo provided"}), 400

    file = request.files["photo"]
    if not file.filename or not allowed_file(file.filename, "image"):
        return jsonify({"error": "Invalid file type. Only images allowed."}), 400

    filename = secure_filename(f"profile_{user_id}_{file.filename}")
    upload_dir = os.path.join(os.getenv("UPLOAD_FOLDER", "uploads"), "profiles")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    try:
        db = get_db()
        db.table("users").update({"profile_photo": file_path}).eq("user_id", user_id).execute()
        return jsonify({"message": "Photo uploaded", "path": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    try:
        db = get_db()
        db.table("chats").delete().eq("user_id", user_id).execute()
        db.table("reports").delete().eq("user_id", user_id).execute()
        db.table("uploads").delete().eq("user_id", user_id).execute()
        db.table("users").delete().eq("user_id", user_id).execute()
        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
