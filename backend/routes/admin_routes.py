from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db
import os

admin_bp = Blueprint("admin", __name__)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@healthbot.com")

def require_admin(user_id):
    db = get_db()
    result = db.table("users").select("email").eq("user_id", user_id).execute()
    if not result.data or result.data[0]["email"] != ADMIN_EMAIL:
        return False
    return True

@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    if not require_admin(user_id):
        return jsonify({"error": "Admin access required"}), 403
    try:
        db = get_db()
        users = db.table("users").select("user_id", count="exact").execute()
        chats = db.table("chats").select("chat_id", count="exact").execute()
        reports = db.table("reports").select("report_id", count="exact").execute()
        uploads = db.table("uploads").select("upload_id", count="exact").execute()
        return jsonify({
            "total_users": users.count,
            "total_chats": chats.count,
            "total_reports": reports.count,
            "total_uploads": uploads.count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_all_users():
    user_id = get_jwt_identity()
    if not require_admin(user_id):
        return jsonify({"error": "Admin access required"}), 403
    try:
        db = get_db()
        result = db.table("users").select("user_id, username, email, age, gender, created_at").order("created_at", desc=True).execute()
        return jsonify({"users": result.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/users/<int:target_user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(target_user_id):
    user_id = get_jwt_identity()
    if not require_admin(user_id):
        return jsonify({"error": "Admin access required"}), 403
    try:
        db = get_db()
        db.table("chats").delete().eq("user_id", target_user_id).execute()
        db.table("reports").delete().eq("user_id", target_user_id).execute()
        db.table("uploads").delete().eq("user_id", target_user_id).execute()
        db.table("users").delete().eq("user_id", target_user_id).execute()
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
