# Quick Fix - uploaded_files Column Error

## Error Message
```
"Could not find the 'uploaded_files' column of 'chats' in the schema cache"
```

## Quick Fix (3 Steps)

### Step 1: Run This SQL in Supabase
1. Go to [Supabase Dashboard](https://supabase.com/dashboard) → Your Project → SQL Editor
2. Paste and run:

```sql
ALTER TABLE chats ADD COLUMN IF NOT EXISTS uploaded_files TEXT DEFAULT NULL;
```

### Step 2: Verify
Run this to confirm:
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'chats' AND column_name = 'uploaded_files';
```

Should return: `uploaded_files`

### Step 3: Restart Backend
```bash
# Stop backend (Ctrl+C)
cd backend
python app.py
```

## Test It Works
```bash
# Test from command line (replace YOUR_TOKEN)
curl -X POST http://localhost:5000/api/chat/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "test message"}'
```

Or use the test script:
```bash
python test_database_fix.py
```

## Done! ✅

Your chat should now work without errors.

---

**Need more details?** See `DATABASE_FIX_GUIDE.md`

**Still having issues?** Check:
- Supabase credentials in `backend/.env`
- Backend is running on port 5000
- You're using the service_role key (not anon key)
