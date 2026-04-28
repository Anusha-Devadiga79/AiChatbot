from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db
from utils.ai_analyzer import (
    generate_health_profile_summary, 
    get_health_insights_and_predictions,
    analyze_advanced_computer_vision
)
from utils.translator import translator
from datetime import datetime, timedelta
import json

health_bp = Blueprint("health", __name__)

@health_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_health_profile():
    """Get comprehensive health profile for user."""
    user_id = get_jwt_identity()
    
    try:
        db = get_db()
        
        # Get user's chat history
        result = db.table("chats").select("*").eq("user_id", user_id).order("timestamp", desc=True).execute()
        
        if not result.data:
            return jsonify({"error": "No health history found"}), 404
        
        # Generate health profile
        profile = generate_health_profile_summary(result.data)
        
        # Get AI insights
        insights = get_health_insights_and_predictions(result.data)
        
        return jsonify({
            "profile": profile,
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_health_analytics():
    """Get predictive health analytics."""
    user_id = get_jwt_identity()
    days = int(request.args.get("days", 30))  # Default to last 30 days
    
    try:
        db = get_db()
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get chat history within date range
        result = db.table("chats").select("*").eq("user_id", user_id).gte("timestamp", start_date.isoformat()).order("timestamp", desc=True).execute()
        
        if not result.data:
            return jsonify({"error": "No recent health data found"}), 404
        
        # Generate analytics
        insights = get_health_insights_and_predictions(result.data)
        profile_summary = generate_health_profile_summary(result.data)
        
        # Calculate trends
        trends = _calculate_health_trends(result.data, days)
        
        return jsonify({
            "analytics": insights,
            "profile_summary": profile_summary,
            "trends": trends,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_bp.route("/advanced-vision", methods=["POST"])
@jwt_required()
def advanced_vision_analysis():
    """Perform advanced computer vision analysis on medical images."""
    user_id = get_jwt_identity()
    
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist("files")
    message = request.form.get("message", "")
    language = request.form.get("language", "en")
    
    # Save uploaded files
    import os
    from werkzeug.utils import secure_filename
    
    upload_dir = os.path.join(os.getenv("UPLOAD_FOLDER", "uploads"), "advanced_vision", str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    image_paths = []
    for file in files:
        if file and file.filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = secure_filename(f"{timestamp}_{file.filename}")
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            image_paths.append(file_path)
    
    if not image_paths:
        return jsonify({"error": "No valid images uploaded"}), 400
    
    try:
        # Translate message if needed
        original_language = language
        if language != "en":
            message = translator.translate_text(message, target_lang="en", source_lang=language)
        
        # Perform advanced vision analysis
        analysis = analyze_advanced_computer_vision(image_paths, message)
        
        # Translate response back if needed
        if original_language != "en" and "response" in analysis:
            analysis["response"] = translator.translate_text(
                analysis["response"], 
                target_lang=original_language, 
                source_lang="en"
            )
        
        # Save analysis to database
        db = get_db()
        insert_data = {
            "user_id": user_id,
            "message": f"[Advanced Vision Analysis] {message}" if message else "[Advanced Vision Analysis]",
            "response": analysis.get("response", "Analysis completed"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        db.table("chats").insert(insert_data).execute()
        
        return jsonify({
            "analysis": analysis,
            "image_count": len(image_paths),
            "language": original_language
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_bp.route("/translate", methods=["POST"])
@jwt_required()
def translate_text():
    """Translate text between languages."""
    data = request.get_json()
    
    if not data or "text" not in data:
        return jsonify({"error": "Text is required"}), 400
    
    text = data["text"]
    target_lang = data.get("target_language", "en")
    source_lang = data.get("source_language")  # Auto-detect if not provided
    
    try:
        # Detect source language if not provided
        if not source_lang:
            source_lang = translator.detect_language(text)
        
        # Translate text
        translated_text = translator.translate_text(text, target_lang=target_lang, source_lang=source_lang)
        
        return jsonify({
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "source_language_name": translator.get_language_name(source_lang),
            "target_language_name": translator.get_language_name(target_lang)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_bp.route("/languages", methods=["GET"])
def get_supported_languages():
    """Get list of supported languages."""
    return jsonify({
        "supported_languages": translator.supported_languages
    }), 200

def _calculate_health_trends(chat_history: list, days: int) -> dict:
    """Calculate health trends from chat history."""
    trends = {
        "symptom_frequency": {},
        "severity_trend": [],
        "consultation_frequency": [],
        "improvement_indicators": []
    }
    
    # Group chats by day
    daily_chats = {}
    for chat in chat_history:
        date_str = chat.get('timestamp', '')[:10]  # Get YYYY-MM-DD
        if date_str not in daily_chats:
            daily_chats[date_str] = []
        daily_chats[date_str].append(chat)
    
    # Calculate daily consultation frequency
    trends["consultation_frequency"] = [
        {"date": date, "count": len(chats)} 
        for date, chats in daily_chats.items()
    ]
    
    # Analyze severity trends over time
    for date, chats in daily_chats.items():
        severity_scores = []
        for chat in chats:
            response = chat.get('response', '').lower()
            if 'severe' in response or 'high' in response:
                severity_scores.append(3)
            elif 'moderate' in response:
                severity_scores.append(2)
            elif 'mild' in response:
                severity_scores.append(1)
        
        if severity_scores:
            avg_severity = sum(severity_scores) / len(severity_scores)
            trends["severity_trend"].append({
                "date": date,
                "average_severity": avg_severity
            })
    
    return trends