import json
import os
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Load symptoms database
def load_symptoms_db():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "symptoms.json")
    with open(data_path, "r") as f:
        return json.load(f)

SYMPTOMS_DB = load_symptoms_db()

def analyze_with_ai(user_input: str, file_content: str = None, user_language: str = "en", user_history: list = None, non_health_count: int = 0) -> dict:
    """Analyze user input with AI — conversational for first 3 messages, health-focused after."""
    from .translator import translator

    original_language = user_language
    if user_language != "en":
        detected_lang = translator.detect_language(user_input)
        if detected_lang != "en":
            user_input, original_language = translator.translate_symptoms_to_english(user_input)

    if not client:
        result = _fallback_analysis(user_input, "no_api_key", user_history)
        if original_language != "en":
            result["response"] = translator.translate_response_to_user_language(result["response"], original_language)
        return result

    try:
        full_input = user_input
        if file_content:
            full_input = f"{user_input}\n\nFile content:\n{file_content}"

        if user_history:
            history_context = "\n\nUser's recent health history:\n"
            for entry in user_history[-5:]:
                history_context += f"- {entry.get('message', '')}: {entry.get('response', '')[:100]}...\n"
            full_input += history_context

        result = _analyze_with_openai(full_input, user_history, non_health_count)

        if original_language != "en":
            result["response"] = translator.translate_response_to_user_language(result["response"], original_language)
            result["original_language"] = original_language

        return result
    except RateLimitError:
        logger.warning("OpenAI rate limit hit, using fallback")
        result = _fallback_analysis(user_input, "rate_limit", user_history)
        if original_language != "en":
            result["response"] = translator.translate_response_to_user_language(result["response"], original_language)
        return result
    except APIConnectionError:
        logger.warning("OpenAI connection error, using fallback")
        result = _fallback_analysis(user_input, "connection", user_history)
        if original_language != "en":
            result["response"] = translator.translate_response_to_user_language(result["response"], original_language)
        return result
    except APIError as e:
        logger.warning(f"OpenAI API error: {str(e)}, using fallback")
        result = _fallback_analysis(user_input, "api_error", user_history)
        if original_language != "en":
            result["response"] = translator.translate_response_to_user_language(result["response"], original_language)
        return result
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        result = _fallback_analysis(user_input, "unknown", user_history)
        if original_language != "en":
            result["response"] = translator.translate_response_to_user_language(result["response"], original_language)
        return result
        result = _fallback_analysis(user_input, "unknown", user_history)
        if original_language != "en":
            result["response"] = translator.translate_response_to_user_language(result["response"], original_language)
        return result

def _is_health_related(text: str) -> bool:
    """Quick check if message is health/symptom related."""
    health_keywords = [
        'pain', 'ache', 'fever', 'cough', 'rash', 'itch', 'sore', 'hurt', 'sick',
        'symptom', 'disease', 'condition', 'infection', 'doctor', 'medicine', 'treatment',
        'headache', 'nausea', 'vomit', 'diarrhea', 'fatigue', 'tired', 'dizzy', 'swollen',
        'bleed', 'wound', 'injury', 'allergy', 'breath', 'chest', 'stomach', 'throat',
        'skin', 'redness', 'swelling', 'burning', 'tingling', 'numbness', 'weakness',
        'diabetes', 'blood', 'pressure', 'heart', 'lung', 'kidney', 'liver', 'cancer',
        'anxiety', 'depression', 'mental', 'health', 'medical', 'hospital', 'clinic',
        'diagnos', 'prescri', 'tablet', 'pill', 'drug', 'vaccine', 'virus', 'bacteria',
        'cold', 'flu', 'covid', 'malaria', 'dengue', 'typhoid', 'acne', 'pimple',
        'dandruff', 'eczema', 'psoriasis', 'asthma', 'migraine', 'ulcer', 'gout'
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in health_keywords)


def _analyze_with_openai(full_input: str, user_history: list = None, non_health_count: int = 0) -> dict:
    """Call OpenAI API — friendly for first 3 messages, then health-focused."""

    # Count how many of the recent messages were non-health
    if non_health_count < 3:
        # Conversational mode — respond naturally but gently steer toward health
        system_content = f"""You are HealthBot AI — a friendly, helpful health assistant. 
You can chat normally and answer general questions, but your specialty is health awareness.

This user has sent {non_health_count} general message(s) so far.
{"Respond naturally to their message." if non_health_count < 2 else "Respond to their message, then gently remind them you're here to help with health questions and symptoms."}

Keep responses concise and warm. If they mention anything health-related, switch to full health analysis mode with structured format:
🏥 Possible Condition | 📋 Description | 🔍 Symptoms | 🟠 Severity | 🛡️ Prevention | ⚕️ When to see doctor

Always end with: ⚠️ For health concerns, always consult a qualified healthcare professional."""
    else:
        # Health-focused mode — nudge them toward health topics
        system_content = """You are HealthBot AI, a health awareness assistant. 
You've been chatting for a while — now gently guide the conversation toward health.

If the message is NOT health-related, respond briefly and then ask:
"By the way, do you have any health concerns or symptoms I can help you with? I can analyze symptoms, skin conditions, and more!"

If the message IS health-related, respond using this exact structured format:

🏥 **Possible Condition: [Name]**

📋 **Description:**
[Clear explanation]

🔍 **Matching Symptoms:**
• [symptom 1]
• [symptom 2]

🟠 **Severity Level:** [Mild / Moderate / High]

🛡️ **Prevention & Management:**
[Specific tips]

⚕️ **When to See a Doctor:**
[Urgency guidance]

🔍 **Other Possible Conditions:**
• [Condition 2]

⚠️ This is for awareness only. Always consult a qualified healthcare professional."""

    models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    last_error = None

    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": full_input}
                ],
                temperature=0.6,
                max_tokens=1200
            )
            ai_response = response.choices[0].message.content
            predictive_insights = _extract_predictive_insights(user_history, ai_response) if user_history else None
            return {
                "matched": True,
                "response": ai_response,
                "model": model,
                "predictive_insights": predictive_insights
            }
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model} failed: {str(e)}, trying next...")
            continue

    raise last_error

def _fallback_analysis(user_input: str, error_type: str = "unknown", user_history: list = None) -> dict:
    """Provide fallback analysis when AI is unavailable — handles greetings + multi-symptom matching."""
    user_lower = user_input.strip().lower()

    # ── Greeting / small talk detection ─────────────────────────────────────
    greetings = {"hi", "hello", "hey", "hii", "helo", "howdy", "sup", "yo", "good morning",
                 "good afternoon", "good evening", "good night", "how are you", "what's up",
                 "whats up", "how r u", "how do you do", "namaste", "hola", "bonjour"}
    if user_lower in greetings or any(user_lower.startswith(g) for g in greetings):
        return {
            "matched": True,
            "response": (
                "👋 Hello! I'm **HealthBot AI** — your personal health awareness assistant.\n\n"
                "I can help you with:\n"
                "• 🤒 Analyzing symptoms and suggesting possible conditions\n"
                "• 🖼️ Analyzing skin conditions or injuries from photos\n"
                "• 💊 Prevention tips and when to see a doctor\n"
                "• 📋 Understanding 50+ health conditions\n\n"
                "**Just describe your symptoms** or upload a photo to get started!\n"
                "For example: *\"I have fever and headache\"* or *\"I have a rash on my arm\"*"
            ),
            "model": "fallback_greeting"
        }

    # ── General questions / non-symptom messages ────────────────────────────
    general_phrases = ["what can you do", "help", "who are you", "what are you",
                       "tell me about", "how does this work", "what is this"]
    if any(p in user_lower for p in general_phrases):
        return {
            "matched": True,
            "response": (
                "🏥 I'm **HealthBot AI**, a disease awareness chatbot.\n\n"
                "**What I can do:**\n"
                "• Analyze your symptoms and suggest possible conditions\n"
                "• Analyze uploaded images (skin rashes, wounds, etc.)\n"
                "• Provide prevention tips and severity assessment\n"
                "• Tell you when to see a doctor\n"
                "• Support 50+ health conditions\n\n"
                "**How to use me:**\n"
                "1. Type your symptoms (e.g. *\"I have fever and sore throat\"*)\n"
                "2. Or upload a photo of a skin condition or injury\n"
                "3. I'll analyze and give you health awareness information\n\n"
                "⚠️ I'm for awareness only — always consult a healthcare professional for diagnosis."
            ),
            "model": "fallback_greeting"
        }

    # ── Symptom matching ─────────────────────────────────────────────────────
    matched_conditions = []

    for key, info in SYMPTOMS_DB.items():
        disease_name = info.get("disease", "").lower()
        symptoms = [s.lower() for s in info.get("symptoms", [])]
        score = 0

        if any(word in user_lower for word in disease_name.split() if len(word) > 3):
            score += 15
        if key.lower() in user_lower:
            score += 20

        for symptom in symptoms:
            if symptom in user_lower:
                score += 6
            else:
                words = [w for w in symptom.split() if len(w) > 3]
                matches = sum(1 for w in words if w in user_lower)
                if matches:
                    score += matches * 2

        if score > 0:
            matched_conditions.append((score, info))

    matched_conditions.sort(key=lambda x: x[0], reverse=True)

    if matched_conditions and matched_conditions[0][0] >= 4:
        condition = matched_conditions[0][1]
        severity = condition.get("severity", "unknown")
        severity_emoji = {"mild": "🟡", "moderate": "🟠", "high": "🔴"}.get(severity, "⚪")

        message = f"🏥 **Possible Condition: {condition.get('disease')}**\n\n"
        message += f"📋 **Description:**\n{condition.get('description')}\n\n"

        symptoms_list = condition.get("symptoms", [])
        if symptoms_list:
            message += "🔍 **Common Symptoms:**\n"
            for s in symptoms_list[:6]:
                message += f"• {s.capitalize()}\n"
            message += "\n"

        message += f"{severity_emoji} **Severity Level:** {severity.capitalize()}\n\n"
        message += f"🛡️ **Prevention & Management:**\n{condition.get('prevention')}\n\n"
        message += f"⚕️ **When to See a Doctor:**\n{condition.get('when_to_see_doctor', 'Consult a doctor if symptoms persist')}\n\n"

        others = [(s, c) for s, c in matched_conditions[1:4] if s >= 4]
        if others:
            message += "🔍 **Other Possible Conditions:**\n"
            for _, other in others:
                message += f"• {other.get('disease')}\n"
            message += "\n"

        return {"matched": True, "response": message, "model": "fallback_database"}

    # ── No match ─────────────────────────────────────────────────────────────
    message = (
        "I'm not sure I understood that. Could you describe your **symptoms** more clearly?\n\n"
        "**Examples:**\n"
        "• \"I have fever, headache and body aches\"\n"
        "• \"I have itchy red rash on my arms\"\n"
        "• \"I have burning sensation when urinating\"\n"
        "• \"I have chest pain and shortness of breath\"\n\n"
        "Or **upload a photo** of a skin condition, rash, or injury and I'll analyze it!\n\n"
        "I can help with 50+ conditions: skin, respiratory, digestive, infections, chronic diseases, and emergencies."
    )
    return {"matched": True, "response": message, "model": "fallback_database"}

def _get_fallback_message(error_type: str) -> str:
    """Get appropriate fallback message based on error type."""
    messages = {
        "no_api_key": "⚠️ AI service not configured. Using symptom database for analysis.",
        "rate_limit": "⚠️ AI service is temporarily busy. Using symptom database for analysis.",
        "connection": "⚠️ Could not connect to AI service. Using symptom database for analysis.",
        "api_error": "⚠️ AI service encountered an error. Using symptom database for analysis.",
        "unknown": "⚠️ Using symptom database for analysis."
    }
    return messages.get(error_type, "Using symptom database for analysis.")

def format_ai_response(analysis: dict) -> str:
    """Format AI response for display."""
    # Handle error dict from failed vision analysis
    if "error" in analysis and "response" not in analysis:
        return (
            "🖼️ I received your image but couldn't fully analyze it right now.\n\n"
            "**Please also describe what you see** in a text message, for example:\n"
            "• \"I have a red rash on my arm\"\n"
            "• \"There's a pimple-like bump on my skin\"\n"
            "• \"I have a wound that looks infected\"\n\n"
            "I'll give you a detailed health analysis based on your description.\n\n"
            "⚠️ This is for awareness purposes only. Always consult a qualified healthcare professional."
        )

    if not analysis.get("matched"):
        return analysis.get("response", "Please describe your symptoms and I'll help you.")

    response = analysis.get("response", "")
    # Don't double-add disclaimer if already present
    if "⚠️" in response and "awareness" in response:
        return response

    disclaimer = "\n\n⚠️ This is for awareness purposes only. Always consult a qualified healthcare professional for proper diagnosis and treatment."
    return response + disclaimer

def analyze_multiple_files(text_input: str, file_paths: list) -> dict:
    """Analyze multiple files together."""
    if not file_paths:
        return analyze_with_ai(text_input)
    
    # For now, just analyze the text input
    # File analysis would require more complex processing
    return analyze_with_ai(text_input)

def extract_structured_data(ai_response: str) -> dict:
    """Extract structured data from AI response."""
    # Try to extract key information from the response
    return {
        "disease": "Based on analysis",
        "description": ai_response[:200] if ai_response else "",
        "symptoms": [],
        "prevention": "Consult healthcare professional",
        "severity": "unknown",
        "when_to_see_doctor": "As soon as possible"
    }

def compare_analyses(analysis1: dict, analysis2: dict) -> dict:
    """Compare two analyses."""
    if not client:
        return {
            "comparison": "AI service not available for comparison.",
            "analysis1": analysis1,
            "analysis2": analysis2
        }
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"""Compare these two medical analyses:

Analysis 1: {json.dumps(analysis1)}

Analysis 2: {json.dumps(analysis2)}

Provide a brief comparison of similarities and differences."""
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "comparison": response.choices[0].message.content,
            "analysis1": analysis1,
            "analysis2": analysis2
        }
    except Exception as e:
        return {
            "comparison": "Could not compare analyses.",
            "analysis1": analysis1,
            "analysis2": analysis2,
            "error": str(e)
        }

def _extract_predictive_insights(user_history: list, current_analysis: str) -> dict:
    """Extract predictive insights from user history."""
    if not user_history or len(user_history) < 2:
        return None
    
    # Analyze patterns in user history
    symptoms_frequency = {}
    conditions_mentioned = []
    severity_trends = []
    
    for entry in user_history:
        message = entry.get('message', '').lower()
        response = entry.get('response', '').lower()
        
        # Count symptom frequency
        common_symptoms = ['fever', 'headache', 'cough', 'fatigue', 'pain', 'nausea', 'dizziness']
        for symptom in common_symptoms:
            if symptom in message:
                symptoms_frequency[symptom] = symptoms_frequency.get(symptom, 0) + 1
        
        # Extract severity mentions
        if 'severe' in response or 'high' in response:
            severity_trends.append('high')
        elif 'moderate' in response:
            severity_trends.append('moderate')
        elif 'mild' in response:
            severity_trends.append('mild')
    
    # Generate insights
    insights = {
        "recurring_symptoms": [symptom for symptom, count in symptoms_frequency.items() if count > 1],
        "symptom_frequency": symptoms_frequency,
        "severity_trend": severity_trends[-3:] if severity_trends else [],
        "risk_factors": [],
        "recommendations": []
    }
    
    # Add risk factor analysis
    if len(insights["recurring_symptoms"]) > 0:
        insights["risk_factors"].append("Recurring symptoms detected - may indicate chronic condition")
        insights["recommendations"].append("Consider comprehensive medical evaluation")
    
    if 'high' in severity_trends[-2:]:
        insights["risk_factors"].append("Recent high-severity symptoms")
        insights["recommendations"].append("Monitor symptoms closely and seek medical attention")
    
    return insights

def analyze_advanced_computer_vision(image_paths: list, message: str = "") -> dict:
    """Advanced computer vision analysis for medical images."""
    if not client:
        return {"error": "AI service not available for advanced vision analysis"}
    
    try:
        # Enhanced vision analysis with medical focus
        content = []
        
        if message:
            content.append({
                "type": "text",
                "text": f"""Perform advanced medical image analysis. User context: {message}

Please provide detailed analysis including:
1. VISUAL ASSESSMENT: Describe what you observe in detail
2. MEDICAL INDICATORS: Identify any visible symptoms, conditions, or abnormalities
3. DIFFERENTIAL DIAGNOSIS: List possible conditions based on visual evidence
4. SEVERITY ASSESSMENT: Rate the apparent severity and urgency
5. RECOMMENDATIONS: Suggest next steps and when to seek medical care
6. PREVENTION: Provide relevant prevention tips
7. FOLLOW-UP: Recommend monitoring or additional tests if needed

Use medical terminology where appropriate but explain in layman's terms."""
            })
        else:
            content.append({
                "type": "text",
                "text": """Perform comprehensive medical image analysis including:
1. Detailed visual description of any visible symptoms or conditions
2. Possible medical conditions based on visual evidence
3. Severity assessment and urgency level
4. Recommended medical actions and timeline
5. Prevention and care recommendations"""
            })
        
        # Add images with enhanced encoding
        for image_path in image_paths:
            try:
                base64_image = encode_image_to_base64(image_path)
                media_type = get_image_media_type(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}",
                        "detail": "high"
                    }
                })
            except Exception as e:
                logger.error(f"Error encoding image {image_path}: {e}")
                continue

        # Try gpt-4o (supports vision), fallback to gpt-4-turbo
        for vision_model in ["gpt-4o", "gpt-4-turbo"]:
            try:
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
                    temperature=0.3,
                    max_tokens=1200
                )
                return {
                    "matched": True,
                    "response": response.choices[0].message.content,
                    "model": vision_model,
                    "analysis_type": "advanced_computer_vision"
                }
            except Exception as e:
                logger.warning(f"Vision model {vision_model} failed: {e}")
                continue

        return {"error": "Vision analysis failed — all models unavailable"}

    except Exception as e:
        logger.error(f"Advanced vision analysis error: {e}")
        return {"error": f"Vision analysis failed: {str(e)}"}


def generate_health_profile_summary(user_history: list, user_data: dict = None) -> dict:
    """Generate comprehensive health profile and history summary."""
    if not user_history:
        return {"error": "No health history available"}
    
    profile = {
        "total_consultations": len(user_history),
        "date_range": {
            "first_consultation": user_history[-1].get('timestamp') if user_history else None,
            "last_consultation": user_history[0].get('timestamp') if user_history else None
        },
        "symptom_patterns": {},
        "condition_history": [],
        "severity_distribution": {"mild": 0, "moderate": 0, "high": 0},
        "health_trends": [],
        "risk_assessment": {},
        "recommendations": []
    }
    
    # Analyze symptom patterns
    all_symptoms = []
    for entry in user_history:
        message = entry.get('message', '').lower()
        response = entry.get('response', '').lower()
        
        # Extract symptoms from messages
        common_symptoms = ['fever', 'headache', 'cough', 'fatigue', 'pain', 'nausea', 'dizziness', 
                          'rash', 'shortness of breath', 'chest pain', 'back pain', 'joint pain']
        
        for symptom in common_symptoms:
            if symptom in message:
                all_symptoms.append(symptom)
                profile["symptom_patterns"][symptom] = profile["symptom_patterns"].get(symptom, 0) + 1
        
        # Extract severity information
        if 'severe' in response or 'high' in response:
            profile["severity_distribution"]["high"] += 1
        elif 'moderate' in response:
            profile["severity_distribution"]["moderate"] += 1
        elif 'mild' in response:
            profile["severity_distribution"]["mild"] += 1
    
    # Generate health trends
    if profile["symptom_patterns"]:
        most_common = max(profile["symptom_patterns"], key=profile["symptom_patterns"].get)
        profile["health_trends"].append(f"Most frequent symptom: {most_common}")
    
    # Risk assessment
    high_severity_ratio = profile["severity_distribution"]["high"] / len(user_history)
    if high_severity_ratio > 0.3:
        profile["risk_assessment"]["high_severity_frequency"] = "Frequent high-severity symptoms detected"
        profile["recommendations"].append("Consider comprehensive medical evaluation")
    
    recurring_symptoms = [s for s, count in profile["symptom_patterns"].items() if count > 2]
    if recurring_symptoms:
        profile["risk_assessment"]["recurring_symptoms"] = recurring_symptoms
        profile["recommendations"].append("Monitor recurring symptoms and discuss with healthcare provider")
    
    return profile

def get_health_insights_and_predictions(user_history: list) -> dict:
    """Generate AI-powered health insights and predictions."""
    if not client or not user_history:
        return {"error": "Insufficient data for health predictions"}
    
    try:
        # Prepare history summary for AI analysis
        history_summary = ""
        for i, entry in enumerate(user_history[-10:]):  # Last 10 entries
            history_summary += f"Entry {i+1}: {entry.get('message', '')}\nResponse: {entry.get('response', '')[:200]}...\n\n"
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a health analytics AI. Analyze the user's health history and provide:

1. PATTERN ANALYSIS: Identify recurring symptoms, conditions, or health patterns
2. RISK ASSESSMENT: Evaluate potential health risks based on history
3. PREDICTIVE INSIGHTS: Suggest what to monitor or be aware of
4. LIFESTYLE RECOMMENDATIONS: Provide personalized health advice
5. PREVENTIVE MEASURES: Suggest specific prevention strategies
6. MONITORING PLAN: Recommend what symptoms or changes to track

Provide actionable, evidence-based insights while maintaining appropriate medical disclaimers."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this health history and provide insights:\n\n{history_summary}"
                }
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        return {
            "insights": response.choices[0].message.content,
            "model": "gpt-4-turbo",
            "analysis_type": "predictive_health_analytics"
        }
        
    except Exception as e:
        logger.error(f"Health insights generation error: {e}")
        return {"error": f"Failed to generate health insights: {str(e)}"}

# Helper function imports for image processing
def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for API."""
    import base64
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