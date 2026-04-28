-- Run this in your Supabase SQL Editor
-- Adds missing columns to the reports table

ALTER TABLE reports ADD COLUMN IF NOT EXISTS extracted_text TEXT DEFAULT '';
ALTER TABLE reports ADD COLUMN IF NOT EXISTS analysis TEXT DEFAULT NULL;
