from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db
from utils.auth_helpers import allowed_file, get_file_type
from werkzeug.utils import secure_filename
from datetime import datetime
import os

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/create", methods=["POST"])
@jwt_required()
def create_upload():
    user_id = get_jwt_identity()
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Check file size (16MB max)
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > 16 * 1024 * 1024:
        return jsonify({"error": "File too large. Max 16MB allowed."}), 400

    file_type = get_file_type(file.filename)
    filename = secure_filename(f"{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    upload_dir = os.path.join(os.getenv("UPLOAD_FOLDER", "uploads"), file_type)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    try:
        db = get_db()
        result = db.table("uploads").insert({
            "user_id": user_id,
            "file_path": file_path,
            "file_type": file_type,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        upload = result.data[0]
        return jsonify({
            "message": "File uploaded successfully",
            "upload_id": upload["upload_id"],
            "file_path": file_path,
            "file_type": file_type
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@upload_bp.route("/get", methods=["GET"])
@jwt_required()
def get_uploads():
    user_id = get_jwt_identity()
    file_type = request.args.get("type")
    try:
        db = get_db()
        query = db.table("uploads").select("*").eq("user_id", user_id).order("created_at", desc=True)
        if file_type:
            query = query.eq("file_type", file_type)
        result = query.execute()
        return jsonify({"uploads": result.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@upload_bp.route("/delete/<int:upload_id>", methods=["DELETE"])
@jwt_required()
def delete_upload(upload_id):
    user_id = get_jwt_identity()
    try:
        db = get_db()
        result = db.table("uploads").select("*").eq("upload_id", upload_id).eq("user_id", user_id).execute()
        if not result.data:
            return jsonify({"error": "Upload not found"}), 404
        file_path = result.data[0].get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        db.table("uploads").delete().eq("upload_id", upload_id).execute()
        return jsonify({"message": "Upload deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
