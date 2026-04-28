-- =============================================
-- AI Public Health Chatbot - Supabase Schema
-- Run this in your Supabase SQL Editor
-- =============================================

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age > 0 AND age < 150),
    gender VARCHAR(20),
    profile_photo TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chats Table
CREATE TABLE IF NOT EXISTS chats (
    chat_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    analysis JSONB DEFAULT NULL,
    uploaded_files TEXT DEFAULT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reports Table
CREATE TABLE IF NOT EXISTS reports (
    report_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    extracted_text TEXT DEFAULT '',
    analysis JSONB DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Uploads Table
CREATE TABLE IF NOT EXISTS uploads (
    upload_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_timestamp ON chats(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
CREATE INDEX IF NOT EXISTS idx_uploads_user_id ON uploads(user_id);

-- Row Level Security (RLS) - Enable for production
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploads ENABLE ROW LEVEL SECURITY;

-- NOTE: Since we use JWT auth in Flask (not Supabase Auth),
-- we use the service role key in backend and manage auth ourselves.
-- For development, you can disable RLS or create permissive policies:

CREATE POLICY "Allow all for service role" ON users FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON chats FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON reports FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON uploads FOR ALL USING (true);
