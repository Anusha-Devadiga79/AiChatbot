-- ONE-LINE FIX for uploaded_files column error
-- Copy this line and run it in Supabase SQL Editor

ALTER TABLE chats ADD COLUMN IF NOT EXISTS uploaded_files TEXT DEFAULT NULL;

-- That's it! Now restart your backend server.
