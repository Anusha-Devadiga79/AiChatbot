#!/usr/bin/env python3
"""
Test script to verify the database fix for uploaded_files column
Run this after applying the migration
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv('backend/.env')

def test_database_connection():
    """Test if we can connect to Supabase"""
    print("Testing database connection...")
    try:
        from utils.db import get_db
        db = get_db()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_chats_table_structure():
    """Test if chats table has the uploaded_files column"""
    print("\nTesting chats table structure...")
    try:
        from utils.db import get_db
        db = get_db()
        
        # Try to query with uploaded_files column
        result = db.table("chats").select("chat_id, message, uploaded_files").limit(1).execute()
        
        print("✅ uploaded_files column exists in chats table")
        
        # Check if we got data
        if result.data:
            chat = result.data[0]
            print(f"   Sample chat_id: {chat.get('chat_id')}")
            print(f"   uploaded_files value: {chat.get('uploaded_files', 'NULL')}")
        else:
            print("   (No chats in database yet)")
        
        return True
    except Exception as e:
        error_msg = str(e)
        if "uploaded_files" in error_msg.lower():
            print(f"❌ uploaded_files column is MISSING from chats table")
            print(f"   Error: {error_msg}")
            print("\n📋 ACTION REQUIRED:")
            print("   1. Go to Supabase SQL Editor")
            print("   2. Run the migration from: database/migration_add_uploaded_files.sql")
            print("   3. Or see: DATABASE_FIX_GUIDE.md for detailed instructions")
            return False
        else:
            print(f"❌ Unexpected error: {error_msg}")
            return False

def test_insert_without_files():
    """Test inserting a chat without uploaded files"""
    print("\nTesting chat insert without files...")
    try:
        from utils.db import get_db
        from datetime import datetime
        
        db = get_db()
        
        # Try to insert a test chat
        test_data = {
            "user_id": 999999,  # Test user ID
            "message": "Test message - database fix verification",
            "response": "Test response",
            "analysis": {"matched": False, "test": True},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = db.table("chats").insert(test_data).execute()
        
        if result.data:
            chat_id = result.data[0].get('chat_id')
            print(f"✅ Successfully inserted test chat (ID: {chat_id})")
            
            # Clean up test data
            db.table("chats").delete().eq("chat_id", chat_id).execute()
            print(f"   Cleaned up test chat")
            return True
        else:
            print("❌ Insert returned no data")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Insert failed: {error_msg}")
        if "uploaded_files" in error_msg.lower():
            print("\n📋 The uploaded_files column issue is still present")
        return False

def test_insert_with_files():
    """Test inserting a chat with uploaded files"""
    print("\nTesting chat insert with files...")
    try:
        from utils.db import get_db
        from datetime import datetime
        
        db = get_db()
        
        # Try to insert a test chat with files
        test_data = {
            "user_id": 999999,  # Test user ID
            "message": "Test message with files",
            "response": "Test response",
            "analysis": {"matched": False, "test": True},
            "uploaded_files": "test_file1.jpg,test_file2.jpg",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = db.table("chats").insert(test_data).execute()
        
        if result.data:
            chat_id = result.data[0].get('chat_id')
            uploaded_files = result.data[0].get('uploaded_files')
            print(f"✅ Successfully inserted test chat with files (ID: {chat_id})")
            print(f"   uploaded_files: {uploaded_files}")
            
            # Clean up test data
            db.table("chats").delete().eq("chat_id", chat_id).execute()
            print(f"   Cleaned up test chat")
            return True
        else:
            print("❌ Insert returned no data")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Insert with files failed: {error_msg}")
        return False

def main():
    print("=" * 60)
    print("DATABASE FIX VERIFICATION TEST")
    print("=" * 60)
    
    # Check environment variables
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Missing environment variables!")
        print("   Make sure backend/.env has SUPABASE_URL and SUPABASE_KEY")
        return
    
    # Run tests
    tests = [
        test_database_connection(),
        test_chats_table_structure(),
        test_insert_without_files(),
        test_insert_with_files()
    ]
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(tests)
    total = len(tests)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("   Your database is properly configured.")
        print("   You can now restart the backend and use the chat feature.")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("   Please follow the instructions in DATABASE_FIX_GUIDE.md")
        print("   to add the uploaded_files column to your database.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
