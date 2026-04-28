#!/usr/bin/env python3
"""
Test script for Advanced Features Implementation
Tests all four advanced features:
1. Multi-Language Support
2. Advanced Computer Vision  
3. Predictive Health Analytics
4. Health Profile & History
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

class AdvancedFeaturesTest:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        
    def authenticate(self):
        """Authenticate and get JWT token."""
        print("🔐 Authenticating...")
        
        # Try to register first (in case user doesn't exist)
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": "Test User"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
            print(f"Registration: {response.status_code}")
        except:
            pass  # User might already exist
        
        # Login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.text}")
            return False
    
    def test_multi_language_support(self):
        """Test Multi-Language Support features."""
        print("\n🌍 Testing Multi-Language Support...")
        
        # Test 1: Get supported languages
        print("📋 Getting supported languages...")
        response = self.session.get(f"{BASE_URL}/health/languages")
        if response.status_code == 200:
            languages = response.json()["supported_languages"]
            print(f"✅ Found {len(languages)} supported languages")
            print(f"   Sample: {list(languages.items())[:5]}")
        else:
            print(f"❌ Failed to get languages: {response.text}")
            return False
        
        # Test 2: Direct translation
        print("🔄 Testing direct translation...")
        translation_data = {
            "text": "I have fever and headache",
            "target_language": "es",
            "source_language": "en"
        }
        
        response = self.session.post(f"{BASE_URL}/health/translate", json=translation_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Translation successful:")
            print(f"   Original: {result['original_text']}")
            print(f"   Translated: {result['translated_text']}")
            print(f"   Languages: {result['source_language_name']} → {result['target_language_name']}")
        else:
            print(f"❌ Translation failed: {response.text}")
            return False
        
        # Test 3: Multi-language chat
        print("💬 Testing multi-language chat...")
        chat_data = {
            "message": "Tengo dolor de cabeza",  # Spanish: "I have headache"
            "language": "es"
        }
        
        response = self.session.post(f"{BASE_URL}/chat/send", json=chat_data)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Multi-language chat successful")
            print(f"   Model used: {result.get('model_used', 'N/A')}")
            print(f"   Response length: {len(result.get('response', ''))}")
        else:
            print(f"❌ Multi-language chat failed: {response.text}")
            return False
        
        return True
    
    def test_advanced_computer_vision(self):
        """Test Advanced Computer Vision features."""
        print("\n👁️ Testing Advanced Computer Vision...")
        
        # Create a test image file (placeholder)
        test_image_path = "test_image.jpg"
        if not os.path.exists(test_image_path):
            print("⚠️ No test image found. Creating placeholder...")
            # Create a simple test image using PIL
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (200, 200), color='white')
                draw = ImageDraw.Draw(img)
                draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
                draw.text((60, 170), "Test Medical Image", fill='black')
                img.save(test_image_path)
                print(f"✅ Created test image: {test_image_path}")
            except ImportError:
                print("❌ PIL not available, skipping vision test")
                return False
        
        # Test advanced vision analysis
        print("🔍 Testing advanced vision analysis...")
        
        files = {'files': open(test_image_path, 'rb')}
        data = {
            'message': 'Please analyze this medical image for any visible conditions',
            'language': 'en'
        }
        
        response = self.session.post(f"{BASE_URL}/health/advanced-vision", files=files, data=data)
        files['files'].close()
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('analysis', {})
            print(f"✅ Advanced vision analysis successful")
            print(f"   Analysis type: {analysis.get('analysis_type', 'N/A')}")
            print(f"   Model used: {analysis.get('model', 'N/A')}")
            print(f"   Response preview: {analysis.get('response', '')[:100]}...")
        else:
            print(f"❌ Advanced vision analysis failed: {response.text}")
            return False
        
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return True
    
    def test_predictive_health_analytics(self):
        """Test Predictive Health Analytics features."""
        print("\n📊 Testing Predictive Health Analytics...")
        
        # Create some chat history for analytics
        print("📝 Creating sample health history...")
        sample_messages = [
            "I have a headache and feel tired",
            "My headache is getting worse",
            "I have fever and body aches", 
            "Feeling better today, just mild fatigue",
            "Headache is back again",
            "I have a cough and sore throat",
            "Still coughing, also have runny nose",
            "Feeling much better now"
        ]
        
        for i, message in enumerate(sample_messages):
            chat_data = {"message": message, "language": "en"}
            response = self.session.post(f"{BASE_URL}/chat/send", json=chat_data)
            if response.status_code == 201:
                print(f"   ✅ Chat {i+1}/8 created")
            else:
                print(f"   ❌ Chat {i+1}/8 failed")
        
        # Test health analytics
        print("📈 Testing health analytics...")
        response = self.session.get(f"{BASE_URL}/health/analytics?days=30")
        
        if response.status_code == 200:
            result = response.json()
            analytics = result.get('analytics', {})
            profile = result.get('profile_summary', {})
            
            print(f"✅ Health analytics successful")
            print(f"   Total consultations: {profile.get('total_consultations', 0)}")
            print(f"   Symptom patterns: {len(profile.get('symptom_patterns', {}))}")
            print(f"   Analysis type: {analytics.get('analysis_type', 'N/A')}")
            
            # Check for predictive insights
            if 'insights' in analytics:
                print(f"   Predictive insights: Available ({len(analytics['insights'])} chars)")
            else:
                print(f"   Predictive insights: Not available")
                
        else:
            print(f"❌ Health analytics failed: {response.text}")
            return False
        
        return True
    
    def test_health_profile_and_history(self):
        """Test Health Profile & History features."""
        print("\n📋 Testing Health Profile & History...")
        
        # Test full health profile
        print("👤 Getting comprehensive health profile...")
        response = self.session.get(f"{BASE_URL}/health/profile")
        
        if response.status_code == 200:
            result = response.json()
            profile = result.get('profile', {})
            insights = result.get('insights', {})
            
            print(f"✅ Health profile retrieved successfully")
            print(f"   Total consultations: {profile.get('total_consultations', 0)}")
            print(f"   Symptom patterns: {profile.get('symptom_patterns', {})}")
            print(f"   Severity distribution: {profile.get('severity_distribution', {})}")
            print(f"   Health trends: {len(profile.get('health_trends', []))}")
            print(f"   Risk assessments: {len(profile.get('risk_assessment', {}))}")
            print(f"   Recommendations: {len(profile.get('recommendations', []))}")
            
            if insights.get('insights'):
                print(f"   AI insights: Available ({len(insights['insights'])} chars)")
            
        else:
            print(f"❌ Health profile failed: {response.text}")
            return False
        
        # Test chat history with analytics
        print("📚 Testing chat history retrieval...")
        response = self.session.get(f"{BASE_URL}/chat/get?limit=20")
        
        if response.status_code == 200:
            result = response.json()
            chats = result.get('chats', [])
            print(f"✅ Chat history retrieved: {len(chats)} entries")
            
            # Check for predictive insights in recent chats
            recent_chat_with_insights = None
            for chat in chats[:3]:  # Check last 3 chats
                if 'predictive_insights' in str(chat):
                    recent_chat_with_insights = chat
                    break
            
            if recent_chat_with_insights:
                print(f"   ✅ Found predictive insights in recent chats")
            else:
                print(f"   ⚠️ No predictive insights found in recent chats")
                
        else:
            print(f"❌ Chat history retrieval failed: {response.text}")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all advanced feature tests."""
        print("🚀 Starting Advanced Features Test Suite")
        print("=" * 50)
        
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        results = {
            "multi_language": self.test_multi_language_support(),
            "computer_vision": self.test_advanced_computer_vision(),
            "predictive_analytics": self.test_predictive_health_analytics(),
            "health_profile": self.test_health_profile_and_history()
        }
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        for feature, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{feature.replace('_', ' ').title()}: {status}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        
        print(f"\nOverall: {total_passed}/{total_tests} tests passed")
        
        if total_passed == total_tests:
            print("🎉 ALL ADVANCED FEATURES ARE WORKING CORRECTLY!")
        else:
            print("⚠️ Some features need attention. Check the logs above.")
        
        return total_passed == total_tests

if __name__ == "__main__":
    tester = AdvancedFeaturesTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)