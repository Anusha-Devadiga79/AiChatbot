from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db
from utils.ai_analyzer import analyze_with_ai, format_ai_response, analyze_multiple_files, extract_structured_data
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import base64
from openai import APIError, RateLimitError, APIConnectionError

chat_bp = Blueprint("chat", __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'avi', 'mov', 'mkv', 'webm'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_media_type(filename: str) -> str:
    """Get media type for image."""
    ext = filename.rsplit('.', 1)[1].lower()
    media_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return media_types.get(ext, 'image/jpeg')

def analyze_images_with_vision(message: str, image_paths: list) -> dict:
    """Analyze images using OpenAI Vision API with fallback."""
    from openai import OpenAI, APIError, RateLimitError, APIConnectionError
    import traceback
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found, using text fallback")
        return analyze_with_ai(message or "Image uploaded - please describe what you see")
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Build message content with images
        content = []
        
        # Add text message
        if message:
            content.append({
                "type": "text",
                "text": f"Analyze this image and help identify symptoms or conditions. User message: {message}"
            })
        else:
            content.append({
                "type": "text",
                "text": "Please analyze this medical image and identify any visible symptoms, skin conditions, or health concerns. Describe what you see and suggest possible conditions."
            })
        
        # Add images
        images_added = 0
        for image_path in image_paths:
            try:
                base64_image = encode_image_to_base64(image_path)
                media_type = get_image_media_type(image_path)
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}"
                    }
                })
                images_added += 1
            except Exception as e:
                print(f"❌ Error encoding image {image_path}: {e}")
                traceback.print_exc()
                continue
        
        if images_added == 0:
            print("❌ No images could be encoded, using text fallback")
            return analyze_with_ai(message or "Image uploaded - please describe your symptoms")
        
        # Try GPT-4o (vision), then gpt-4-turbo as fallback
        for vision_model in ["gpt-4o", "gpt-4-turbo"]:
            try:
                print(f"🔄 Attempting image analysis with {vision_model}")
                response = client.chat.completions.create(
                    model=vision_model,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are HealthBot AI. Analyze the medical image and respond using this format:

🏥 **Visual Assessment:**
[Describe exactly what you see]

📋 **Possible Condition:**
[Most likely condition based on visual evidence]

🔍 **Observed Indicators:**
• [indicator 1]
• [indicator 2]

🟠 **Severity:** [Mild / Moderate / High]

🛡️ **Care & Prevention:**
[Specific advice]

⚕️ **When to See a Doctor:**
[Urgency guidance]

⚠️ This is for awareness only. Always consult a qualified healthcare professional."""
                        },
                        {"role": "user", "content": content}
                    ],
                    temperature=0.4,
                    max_tokens=1000
                )
                print(f"✅ Image analysis successful with {vision_model}")
                return {
                    "matched": True,
                    "response": response.choices[0].message.content,
                    "model": vision_model
                }
            except Exception as e:
                print(f"❌ {vision_model} failed: {type(e).__name__}: {str(e)}")
                continue

        # Final fallback to text analysis
        text_prompt = message or "Image uploaded for analysis. Please describe what you see in the image."
        return analyze_with_ai(text_prompt)
    except Exception as e:
        print(f"❌ Image analysis error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        # Final fallback to text analysis
        return analyze_with_ai(message or "Image uploaded - please describe your symptoms in text")

@chat_bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    
    # Handle both JSON and multipart form data
    message = ""
    uploaded_files = []
    file_info_list = []
    image_files = []
    user_language = "en"  # Default language
    
    if request.is_json:
        data = request.get_json()
        message = data.get("message", "").strip()
        user_language = data.get("language", "en")
    else:
        message = request.form.get("message", "").strip()
        user_language = request.form.get("language", "en")
        
        # Handle file uploads
        if "files" in request.files:
            files = request.files.getlist("files")
            upload_dir = os.path.join(os.getenv("UPLOAD_FOLDER", "uploads"), "chat_files", str(user_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                    filename = secure_filename(f"{timestamp}_{file.filename}")
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    uploaded_files.append(file_path)
                    
                    file_info_list.append({
                        "filename": filename,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "type": file.content_type
                    })
                    
                    # Track image files for vision analysis
                    if is_image(filename):
                        image_files.append(file_path)

    if not message and not uploaded_files:
        return jsonify({"error": "Message or files required"}), 400

    try:
        db = get_db()
        
        # Get user's recent history
        history_result = db.table("chats").select("*").eq("user_id", user_id).order("timestamp", desc=True).limit(10).execute()
        user_history = history_result.data if history_result.data else []

        # Count consecutive non-health messages in recent history (session context)
        from utils.ai_analyzer import _is_health_related
        non_health_count = 0
        for entry in user_history[:6]:  # look at last 6 messages
            if not _is_health_related(entry.get("message", "")):
                non_health_count += 1
            else:
                break  # stop counting once we hit a health message

        # Analyze with AI
        if image_files:
            # Vision analysis — use the actual saved image files
            from utils.ai_analyzer import analyze_advanced_computer_vision
            analysis_message = message if message else "Analyze this image for any visible health conditions, skin issues, rashes, wounds, or medical concerns. Describe what you see and suggest possible conditions."

            from utils.translator import translator
            if user_language != "en":
                analysis_message = translator.translate_text(analysis_message, target_lang="en", source_lang=user_language)

            analysis = analyze_advanced_computer_vision(image_files, analysis_message)

            # If vision returned an error, fall back to text analysis with image context
            if "error" in analysis and "response" not in analysis:
                fallback_prompt = message if message else "I uploaded an image showing a health condition. Please provide general guidance on common visible conditions like skin rashes, acne, wounds, or infections."
                analysis = analyze_with_ai(fallback_prompt, user_language=user_language, user_history=user_history, non_health_count=0)

            if user_language != "en" and "response" in analysis:
                analysis["response"] = translator.translate_text(analysis["response"], target_lang=user_language, source_lang="en")

        elif uploaded_files:
            analysis = analyze_multiple_files(message, uploaded_files)
        else:
            analysis = analyze_with_ai(
                message,
                file_content=None,
                user_language=user_language,
                user_history=user_history,
                non_health_count=non_health_count
            )
        
        response_text = format_ai_response(analysis)
        
        # Extract structured data from response
        try:
            structured_data = extract_structured_data(response_text)
        except:
            structured_data = {}
        
        # Prepare insert data - ONLY use columns that exist in original schema
        insert_data = {
            "user_id": user_id,
            "message": message if message else f"[Uploaded {len(uploaded_files)} file(s)]",
            "response": response_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = db.table("chats").insert(insert_data).execute()

        if not result.data:
            return jsonify({"error": "Failed to save chat"}), 500

        chat = result.data[0]
        return jsonify({
            "chat_id": chat.get("chat_id"),
            "message": message if message else f"[Uploaded {len(uploaded_files)} file(s)]",
            "response": response_text,
            "analysis": analysis,
            "structured_data": structured_data,
            "uploaded_files": file_info_list,
            "timestamp": chat.get("timestamp"),
            "language": user_language,
            "predictive_insights": analysis.get("predictive_insights"),
            "model_used": analysis.get("model")
        }), 201
    except Exception as e:
        error_msg = str(e)
        print(f"Chat send error: {error_msg}")
        return jsonify({"error": error_msg}), 500

@chat_bp.route("/get", methods=["GET"])
@jwt_required()
def get_chats():
    user_id = get_jwt_identity()
    search = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    offset = (page - 1) * limit

    try:
        db = get_db()
        query = db.table("chats").select("*").eq("user_id", user_id).order("timestamp", desc=True)

        if search:
            query = query.ilike("message", f"%{search}%")

        result = query.range(offset, offset + limit - 1).execute()
        
        return jsonify({"chats": result.data, "page": page, "limit": limit}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/delete/<int:chat_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(chat_id):
    user_id = get_jwt_identity()
    try:
        db = get_db()
        result = db.table("chats").select("chat_id").eq("chat_id", chat_id).eq("user_id", user_id).execute()
        if not result.data:
            return jsonify({"error": "Chat not found"}), 404
        
        db.table("chats").delete().eq("chat_id", chat_id).execute()
        return jsonify({"message": "Chat deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/delete-all", methods=["DELETE"])
@jwt_required()
def delete_all_chats():
    user_id = get_jwt_identity()
    try:
        db = get_db()
        db.table("chats").delete().eq("user_id", user_id).execute()
        return jsonify({"message": "All chats deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/compare/<int:chat_id1>/<int:chat_id2>", methods=["GET"])
@jwt_required()
def compare_chats(chat_id1, chat_id2):
    """Compare two chat analyses."""
    user_id = get_jwt_identity()
    try:
        db = get_db()
        
        # Get both chats
        result1 = db.table("chats").select("*").eq("chat_id", chat_id1).eq("user_id", user_id).execute()
        result2 = db.table("chats").select("*").eq("chat_id", chat_id2).eq("user_id", user_id).execute()
        
        if not result1.data or not result2.data:
            return jsonify({"error": "One or both chats not found"}), 404
        
        chat1 = result1.data[0]
        chat2 = result2.data[0]
        
        # Create comparison
        from utils.ai_analyzer import compare_analyses
        comparison = compare_analyses({}, {})
        
        return jsonify({
            "chat1": {
                "id": chat_id1,
                "message": chat1["message"],
                "response": chat1["response"]
            },
            "chat2": {
                "id": chat_id2,
                "message": chat2["message"],
                "response": chat2["response"]
            },
            "comparison": comparison
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
