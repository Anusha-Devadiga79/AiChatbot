from deep_translator import GoogleTranslator
import json
import os

class MultiLanguageSupport:
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='en')
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'bn': 'Bengali',
            'ur': 'Urdu',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'gu': 'Gujarati',
            'pa': 'Punjabi',
            'mr': 'Marathi',
            'ne': 'Nepali',
            'si': 'Sinhala',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay',
            'tl': 'Filipino',
            'sw': 'Swahili',
            'am': 'Amharic',
            'tr': 'Turkish',
            'fa': 'Persian',
            'he': 'Hebrew',
            'pl': 'Polish',
            'cs': 'Czech',
            'sk': 'Slovak',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'bg': 'Bulgarian',
            'hr': 'Croatian',
            'sr': 'Serbian',
            'sl': 'Slovenian',
            'et': 'Estonian',
            'lv': 'Latvian',
            'lt': 'Lithuanian',
            'fi': 'Finnish',
            'da': 'Danish',
            'no': 'Norwegian',
            'sv': 'Swedish',
            'is': 'Icelandic',
            'nl': 'Dutch',
            'af': 'Afrikaans'
        }
        
    def detect_language(self, text):
        """Detect the language of input text."""
        try:
            detection = self.translator.detect(text)
            return detection.lang
        except Exception as e:
            print(f"Language detection error: {e}")
            return 'en'  # Default to English
    
    def translate_text(self, text, target_lang='en', source_lang=None):
        """Translate text to target language."""
        try:
            if source_lang:
                result = self.translator.translate(text, src=source_lang, dest=target_lang)
            else:
                translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    def translate_symptoms_to_english(self, symptoms_text):
        """Translate user symptoms to English for analysis."""
        detected_lang = self.detect_language(symptoms_text)
        if detected_lang != 'en':
            return self.translate_text(symptoms_text, target_lang='en', source_lang=detected_lang), detected_lang
        return symptoms_text, 'en'
    
    def translate_response_to_user_language(self, response_text, user_language):
        """Translate AI response back to user's language."""
        if user_language != 'en':
            return self.translate_text(response_text, target_lang=user_language, source_lang='en')
        return response_text
    
    def get_language_name(self, lang_code):
        """Get language name from code."""
        return self.supported_languages.get(lang_code, 'Unknown')

# Global translator instance
translator = MultiLanguageSupport()
