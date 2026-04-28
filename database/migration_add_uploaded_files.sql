-- =============================================
-- Migration: Add uploaded_files column to chats table
-- Safe migration that preserves existing data
-- =============================================

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
