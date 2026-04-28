from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db
from utils.export_helper import generate_pdf_export, generate_doc_export, generate_json_export, generate_csv_export, generate_report_pdf, generate_report_doc

export_bp = Blueprint("export", __name__)

def _get_user_and_chats(user_id, chat_ids=None):
    db = get_db()
    user_res = db.table("users").select("username, email").eq("user_id", user_id).execute()
    user_info = user_res.data[0] if user_res.data else {"username": "User"}
    
    if chat_ids:
        # Export specific chats
        chats = []
        for chat_id in chat_ids:
            result = db.table("chats").select("*").eq("chat_id", chat_id).eq("user_id", user_id).is_("deleted_at", "null").execute()
            if result.data:
                chats.extend(result.data)
    else:
        # Export all chats (excluding soft-deleted)
        chats_res = db.table("chats").select("*").eq("user_id", user_id).is_("deleted_at", "null").order("timestamp", desc=False).execute()
        chats = chats_res.data
    
    return user_info, chats

@export_bp.route("/pdf", methods=["POST", "GET"])
@jwt_required()
def export_pdf():
    user_id = get_jwt_identity()
    try:
        chat_ids = None
        if request.method == "POST":
            data = request.get_json()
            chat_ids = data.get("chat_ids")
        
        user_info, chats = _get_user_and_chats(user_id, chat_ids)
        if not chats:
            return jsonify({"error": "No chat history to export"}), 404

        pdf_bytes = generate_pdf_export(chats, user_info)
        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename=health_report_{user_id}.pdf"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/doc", methods=["POST", "GET"])
@jwt_required()
def export_doc():
    user_id = get_jwt_identity()
    try:
        chat_ids = None
        if request.method == "POST":
            data = request.get_json()
            chat_ids = data.get("chat_ids")
        
        user_info, chats = _get_user_and_chats(user_id, chat_ids)
        if not chats:
            return jsonify({"error": "No chat history to export"}), 404

        doc_bytes = generate_doc_export(chats, user_info)
        response = make_response(doc_bytes)
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        response.headers["Content-Disposition"] = f"attachment; filename=health_report_{user_id}.docx"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/json", methods=["POST", "GET"])
@jwt_required()
def export_json():
    user_id = get_jwt_identity()
    try:
        chat_ids = None
        if request.method == "POST":
            data = request.get_json()
            chat_ids = data.get("chat_ids")
        
        user_info, chats = _get_user_and_chats(user_id, chat_ids)
        if not chats:
            return jsonify({"error": "No chat history to export"}), 404

        json_bytes = generate_json_export(chats, user_info)
        response = make_response(json_bytes)
        response.headers["Content-Type"] = "application/json"
        response.headers["Content-Disposition"] = f"attachment; filename=health_data_{user_id}.json"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/csv", methods=["POST", "GET"])
@jwt_required()
def export_csv():
    user_id = get_jwt_identity()
    try:
        chat_ids = None
        if request.method == "POST":
            data = request.get_json()
            chat_ids = data.get("chat_ids")
        
        user_info, chats = _get_user_and_chats(user_id, chat_ids)
        if not chats:
            return jsonify({"error": "No chat history to export"}), 404

        csv_bytes = generate_csv_export(chats, user_info)
        response = make_response(csv_bytes)
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = f"attachment; filename=health_data_{user_id}.csv"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@export_bp.route("/report/pdf/<int:report_id>", methods=["GET", "POST"])
@jwt_required()
def export_report_pdf(report_id):
    """Export medical report summary as PDF — accepts full content via POST body."""
    user_id = get_jwt_identity()
    try:
        # Accept content from POST body (preferred) or fall back to reading the file
        if request.method == "POST":
            body = request.get_json() or {}
            summary_content = body.get("summary", "")
            prev_content   = body.get("previous", "")
            curr_content   = body.get("current", "")
            language       = body.get("language", "English")
            prev_name      = body.get("prev_name", "Previous Report")
            curr_name      = body.get("curr_name", "Current Report")
        else:
            summary_content = ""
            prev_content    = ""
            curr_content    = ""
            language        = request.args.get("language", "English")
            prev_name       = "Previous Report"
            curr_name       = "Current Report"

        # Verify the report belongs to this user
        db = get_db()
        result = db.table("reports").select("report_id, file_path").eq("report_id", report_id).eq("user_id", user_id).execute()
        if not result.data:
            return jsonify({"error": "Report not found"}), 404

        # If no content passed, extract from file
        if not summary_content and not curr_content:
            from utils.pdf_extractor import extract_text_from_pdf
            path = result.data[0].get("file_path", "")
            import os
            if path.lower().endswith(".pdf") and os.path.exists(path):
                ext = extract_text_from_pdf(path)
                curr_content = ext.get("text", "") if ext.get("success") else ""

        pdf_bytes = generate_report_pdf(
            summary=summary_content,
            previous=prev_content,
            current=curr_content,
            language=language,
            prev_name=prev_name,
            curr_name=curr_name
        )
        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename=health_summary_{report_id}.pdf"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@export_bp.route("/report/doc/<int:report_id>", methods=["GET", "POST"])
@jwt_required()
def export_report_doc(report_id):
    """Export medical report summary as DOCX — accepts full content via POST body."""
    user_id = get_jwt_identity()
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            summary_content = body.get("summary", "")
            prev_content   = body.get("previous", "")
            curr_content   = body.get("current", "")
            language       = body.get("language", "English")
            prev_name      = body.get("prev_name", "Previous Report")
            curr_name      = body.get("curr_name", "Current Report")
        else:
            summary_content = ""
            prev_content    = ""
            curr_content    = ""
            language        = request.args.get("language", "English")
            prev_name       = "Previous Report"
            curr_name       = "Current Report"

        db = get_db()
        result = db.table("reports").select("report_id, file_path").eq("report_id", report_id).eq("user_id", user_id).execute()
        if not result.data:
            return jsonify({"error": "Report not found"}), 404

        if not summary_content and not curr_content:
            from utils.pdf_extractor import extract_text_from_pdf
            path = result.data[0].get("file_path", "")
            import os
            if path.lower().endswith(".pdf") and os.path.exists(path):
                ext = extract_text_from_pdf(path)
                curr_content = ext.get("text", "") if ext.get("success") else ""

        doc_bytes = generate_report_doc(
            summary=summary_content,
            previous=prev_content,
            current=curr_content,
            language=language,
            prev_name=prev_name,
            curr_name=curr_name
        )
        response = make_response(doc_bytes)
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        response.headers["Content-Disposition"] = f"attachment; filename=health_summary_{report_id}.docx"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
