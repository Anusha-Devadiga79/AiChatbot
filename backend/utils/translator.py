from deep_translator import GoogleTranslator

class MultiLanguageSupport:
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'hi': 'Hindi',
            'kn': 'Kannada',
            'ta': 'Tamil',
            'te': 'Telugu'
        }

    def detect_language(self, text):
        # deep-translator does not support detection properly
        return "en"

    def translate_text(self, text, target_lang='en'):
        try:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def translate_symptoms_to_english(self, text):
        return self.translate_text(text, target_lang='en'), 'en'

    def translate_response_to_user_language(self, text, user_language):
        if user_language != 'en':
            return self.translate_text(text, target_lang=user_language)
        return text

    def get_language_name(self, code):
        return self.supported_languages.get(code, 'Unknown')


# global instance
translator = MultiLanguageSupport()
