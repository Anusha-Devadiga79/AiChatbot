# Database Fix Guide - uploaded_files Column

## Problem
Error: "Could not find the 'uploaded_files' column of 'chats' in the schema cache"

This occurs because the `uploaded_files` column doesn't exist in your existing Supabase database, even though it's defined in the schema file.

## Solution

### Step 1: Run the Migration SQL

Go to your Supabase dashboard and execute the migration:

1. Open [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **SQL Editor** (left sidebar)
4. Click **New Query**
5. Copy and paste the following SQL:

```sql
-- Add uploaded_files column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'chats' 
        AND column_name = 'uploaded_files'
    ) THEN
        ALTER TABLE chats 
        ADD COLUMN uploaded_files TEXT DEFAULT NULL;
        
        RAISE NOTICE 'Column uploaded_files added successfully to chats table';
    ELSE
        RAISE NOTICE 'Column uploaded_files already exists in chats table';
    END IF;
END $$;

-- Verify the column was added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'chats'
ORDER BY ordinal_position;
```

6. Click **Run** (or press Ctrl+Enter)
7. You should see a success message

### Step 2: Verify the Column Exists

Run this query to confirm:

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'chats'
AND column_name = 'uploaded_files';
```

Expected output:
```
column_name      | data_type | is_nullable | column_default
uploaded_files   | text      | YES         | NULL
```

### Step 3: Restart Backend

```bash
# Stop the backend (Ctrl+C in the terminal)

# Restart it
cd backend
python app.py
```

### Step 4: Test Chat Functionality

Test that everything works:

**Test 1: Send a text message**
```bash
curl -X POST http://localhost:5000/api/chat/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache"}'
```

**Test 2: Get chat history**
```bash
curl -X GET http://localhost:5000/api/chat/get \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Test 3: Send with file upload (if testing from frontend)**
- Upload an image through the chat interface
- Verify it saves without errors

## Why This Happened

The `schema.sql` file includes the `uploaded_files` column, but:
1. Your database was created before this column was added to the schema
2. Running `CREATE TABLE IF NOT EXISTS` doesn't add new columns to existing tables
3. You need an `ALTER TABLE` migration to add columns to existing tables

## What This Fix Does

✅ **Safe Migration**: Uses `IF NOT EXISTS` check to avoid errors if column already exists
✅ **Preserves Data**: Doesn't drop or recreate the table
✅ **Null-Safe**: Sets default to NULL so existing rows work fine
✅ **Backward Compatible**: Old chats without files will have NULL in this column

## Verification Checklist

After running the migration, verify:

- [ ] Migration SQL executed without errors
- [ ] Column appears in verification query
- [ ] Backend starts without errors
- [ ] Can send text messages
- [ ] Can retrieve chat history
- [ ] Old chats still display correctly
- [ ] New chats save successfully
- [ ] File uploads work (if testing)

## Troubleshooting

### Error: "relation 'chats' does not exist"
**Solution**: Run the full schema first:
```sql
-- Run the entire database/schema.sql file
```

### Error: "column 'uploaded_files' already exists"
**Solution**: This is fine! The migration is idempotent. The column exists and you're good to go.

### Backend still shows error after migration
**Solution**: 
1. Restart the backend server
2. Clear any caching in Supabase (refresh the page)
3. Verify the column exists with the verification query

### Old chats don't show
**Solution**: This shouldn't happen, but if it does:
```sql
-- Check if data is still there
SELECT chat_id, user_id, message, uploaded_files 
FROM chats 
LIMIT 10;
```

All old chats should have `uploaded_files = NULL`, which is correct.

## Alternative: Full Schema Recreation (NOT RECOMMENDED)

⚠️ **WARNING**: This will delete all existing data!

Only use if you have no important data:

```sql
-- DANGER: This deletes all chats!
DROP TABLE IF EXISTS chats CASCADE;

-- Then run the full schema.sql file
```

## Backend Code Safety

The backend code already handles null values properly:

```python
# In chat_routes.py
file_paths_str = ",".join(uploaded_files) if uploaded_files else None

# This means:
# - If files uploaded: "file1.jpg,file2.jpg"
# - If no files: None (NULL in database)
```

When retrieving:
```python
uploaded_files = chat.get('uploaded_files')
if uploaded_files:
    files_list = uploaded_files.split(',')
else:
    files_list = []
```

This handles both NULL and empty string cases safely.

## Summary

1. ✅ Run migration SQL in Supabase SQL Editor
2. ✅ Verify column exists
3. ✅ Restart backend
4. ✅ Test chat functionality
5. ✅ Existing data preserved
6. ✅ New features work

**No frontend changes needed!**
**No data loss!**
**Backward compatible!**

---

If you encounter any issues, check:
1. Supabase connection (SUPABASE_URL and SUPABASE_KEY in .env)
2. Backend logs for specific errors
3. Browser console for frontend errors
4. Database permissions (service_role key should have full access)
