import json
import os
import re

_dataset = None

def load_dataset():
    global _dataset
    if _dataset is None:
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "symptoms.json")
        with open(data_path, "r") as f:
            _dataset = json.load(f)
    return _dataset

def analyze_symptoms(text: str) -> dict:
    """Match user input against symptom dataset using keyword matching."""
    dataset = load_dataset()
    text_lower = text.lower()
    
    matches = []
    
    for keyword, info in dataset.items():
        # Check primary keyword
        if keyword in text_lower:
            matches.append((keyword, info, 2))  # weight 2 for primary match
            continue
        
        # Check symptom list
        symptom_matches = sum(1 for s in info.get("symptoms", []) if s in text_lower)
        if symptom_matches > 0:
            matches.append((keyword, info, symptom_matches))
    
    if not matches:
        return {
            "matched": False,
            "message": "I couldn't identify specific symptoms from your description. Please describe your symptoms more clearly or consult a healthcare professional.",
            "general_advice": "For any health concerns, please consult a qualified medical professional. This chatbot provides general awareness information only."
        }
    
    # Sort by match weight, take top match
    matches.sort(key=lambda x: x[2], reverse=True)
    top_keyword, top_info, _ = matches[0]
    
    # Build additional matches
    other_conditions = []
    for kw, info, _ in matches[1:3]:
        other_conditions.append(info["disease"])
    
    response = {
        "matched": True,
        "disease": top_info["disease"],
        "description": top_info["description"],
        "symptoms": top_info.get("symptoms", []),
        "prevention": top_info["prevention"],
        "severity": top_info.get("severity", "unknown"),
        "when_to_see_doctor": top_info.get("when_to_see_doctor", "Consult a doctor if symptoms persist."),
        "other_possible_conditions": other_conditions,
        "disclaimer": "⚠️ This is for awareness purposes only. Always consult a qualified healthcare professional for proper diagnosis and treatment."
    }
    
    return response

def analyze_extracted_text(text: str) -> dict:
    """Analyze text extracted from PDF reports."""
    return analyze_symptoms(text)

def format_response(analysis: dict) -> str:
    """Format analysis result into readable chat response."""
    if not analysis.get("matched"):
        return f"{analysis['message']}\n\n{analysis.get('general_advice', '')}"
    
    severity_emoji = {"mild": "🟡", "moderate": "🟠", "high": "🔴"}.get(analysis["severity"], "⚪")
    
    response = f"""🏥 **Possible Condition: {analysis['disease']}**

📋 **Description:**
{analysis['description']}

{severity_emoji} **Severity Level:** {analysis['severity'].capitalize()}

🛡️ **Prevention & Management:**
{analysis['prevention']}

⚕️ **When to See a Doctor:**
{analysis['when_to_see_doctor']}

{f"🔍 **Other Possible Conditions:** {', '.join(analysis['other_possible_conditions'])}" if analysis['other_possible_conditions'] else ""}

{analysis['disclaimer']}"""
    
    return response.strip()
