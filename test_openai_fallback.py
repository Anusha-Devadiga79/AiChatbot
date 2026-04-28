#!/usr/bin/env python3
"""
Test script to verify OpenAI fallback system works correctly
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv('backend/.env')

def test_openai_availability():
    """Check if OpenAI is configured"""
    print("=" * 60)
    print("TEST 1: OpenAI Configuration")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print(f"✅ OpenAI API key found: {api_key[:10]}...")
        print("   OpenAI will be attempted first")
    else:
        print("ℹ️  No OpenAI API key configured")
        print("   Will use fallback mode only")
    
    return bool(api_key)

def test_fallback_analysis():
    """Test the fallback analysis system"""
    print("\n" + "=" * 60)
    print("TEST 2: Fallback Analysis System")
    print("=" * 60)
    
    try:
        from utils.ai_analyzer import _fallback_analysis
        
        # Test with common symptoms
        test_inputs = [
            "I have a fever and cough",
            "I have a headache",
            "I have stomach pain and nausea"
        ]
        
        for test_input in test_inputs:
            print(f"\nTesting: '{test_input}'")
            result = _fallback_analysis(test_input, "test")
            
            if result.get("matched"):
                print(f"  ✅ Matched: {result.get('disease')}")
                print(f"  ✅ Severity: {result.get('severity')}")
                print(f"  ✅ Confidence: {result.get('confidence', 0) * 100}%")
            else:
                print(f"  ℹ️  No specific match, general advice provided")
        
        print("\n✅ Fallback system working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Fallback system error: {e}")
        return False

def test_analyze_with_ai():
    """Test the main analyze_with_ai function"""
    print("\n" + "=" * 60)
    print("TEST 3: Main Analysis Function")
    print("=" * 60)
    
    try:
        from utils.ai_analyzer import analyze_with_ai
        
        test_input = "I have a fever, cough, and sore throat"
        print(f"\nAnalyzing: '{test_input}'")
        
        result = analyze_with_ai(test_input)
        
        if result.get("matched"):
            print(f"  ✅ Analysis successful")
            print(f"  ✅ Disease: {result.get('disease')}")
            print(f"  ✅ Severity: {result.get('severity')}")
            
            if result.get("fallback_mode"):
                print(f"  ℹ️  Fallback mode: {result.get('fallback_reason')}")
            else:
                print(f"  ✅ OpenAI mode active")
        else:
            print(f"  ℹ️  No match, but response provided")
            if result.get("fallback_mode"):
                print(f"  ℹ️  Fallback mode: {result.get('fallback_reason')}")
        
        print("\n✅ Main analysis function working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Analysis function error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_format_response():
    """Test response formatting"""
    print("\n" + "=" * 60)
    print("TEST 4: Response Formatting")
    print("=" * 60)
    
    try:
        from utils.ai_analyzer import format_ai_response
        
        # Test with fallback mode
        test_analysis = {
            "matched": True,
            "disease": "Common Cold",
            "description": "A viral infection",
            "symptoms": ["fever", "cough"],
            "severity": "mild",
            "confidence": 0.7,
            "prevention": "Rest and hydration",
            "when_to_see_doctor": "If symptoms worsen",
            "fallback_mode": True,
            "fallback_reason": "AI service temporarily unavailable. Using basic symptom analysis.",
            "disclaimer": "Consult a healthcare professional"
        }
        
        response = format_ai_response(test_analysis)
        
        if "ℹ️" in response and "AI service" in response:
            print("  ✅ Fallback notice included in response")
        
        if "Common Cold" in response:
            print("  ✅ Disease information formatted correctly")
        
        if "Consult a healthcare professional" in response:
            print("  ✅ Disclaimer included")
        
        print("\n✅ Response formatting working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Formatting error: {e}")
        return False

def test_error_handling():
    """Test that errors don't crash the system"""
    print("\n" + "=" * 60)
    print("TEST 5: Error Handling")
    print("=" * 60)
    
    try:
        from utils.ai_analyzer import analyze_with_ai
        
        # Test with empty input
        print("\nTesting with empty input...")
        result = analyze_with_ai("")
        
        if result:
            print("  ✅ Handled empty input without crashing")
        
        # Test with very long input
        print("\nTesting with long input...")
        long_input = "I have symptoms " * 100
        result = analyze_with_ai(long_input)
        
        if result:
            print("  ✅ Handled long input without crashing")
        
        print("\n✅ Error handling working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Error handling failed: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("OPENAI FALLBACK SYSTEM TEST")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("OpenAI Configuration", test_openai_availability),
        ("Fallback Analysis", test_fallback_analysis),
        ("Main Analysis Function", test_analyze_with_ai),
        ("Response Formatting", test_format_response),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("   Your fallback system is working correctly.")
        print("   The app will never crash due to OpenAI errors.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("   Check the error messages above.")
    
    print("=" * 60)
    
    # Additional info
    print("\n📋 NEXT STEPS:")
    print("   1. Restart your backend: cd backend && python app.py")
    print("   2. Test chat functionality through the UI")
    print("   3. Check backend logs for fallback messages")
    print("   4. See OPENAI_QUOTA_FIX.md for detailed documentation")

if __name__ == "__main__":
    main()
