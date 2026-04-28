# Quick Setup Guide

## Prerequisites
- Python 3.8 or higher
- OpenAI API key with GPT-4 access
- Supabase account
- Modern web browser

## Step-by-Step Setup

### 1. Clone or Download the Project
```bash
cd health-chatbot
```

### 2. Database Setup (Supabase)

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Wait for the project to be ready (2-3 minutes)
4. Go to **SQL Editor** in the left sidebar
5. Click **New Query**
6. Copy the entire contents of `database/schema.sql`
7. Paste into the SQL editor and click **Run**
8. Go to **Settings** → **API**
9. Copy your **Project URL** and **service_role key** (not anon key!)

### 3. OpenAI API Setup

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (starts with `sk-`)
6. **Important**: Ensure you have GPT-4 access enabled

### 4. Backend Configuration

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux

# Edit .env file with your credentials
```

**Edit `backend/.env` file:**
```env
# Replace with your Supabase URL
SUPABASE_URL=https://your-project.supabase.co

# Replace with your Supabase service_role key
SUPABASE_KEY=your-service-role-key-here

# Replace with your OpenAI API key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Generate a random secret key (or use any random string)
JWT_SECRET_KEY=your-random-secret-key-minimum-32-characters

# Keep these as is
FLASK_ENV=development
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
ADMIN_EMAIL=admin@healthbot.com
```

### 5. Start the Backend Server

```bash
# Make sure you're in the backend folder with venv activated
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### 6. Start the Frontend

**Option A: Using Python HTTP Server**
```bash
# Open a new terminal (keep backend running)
# Navigate to project root
python -m http.server 8080

# Open browser to:
# http://localhost:8080/frontend/pages/index.html
```

**Option B: Using VS Code Live Server**
1. Install "Live Server" extension in VS Code
2. Right-click on `frontend/pages/index.html`
3. Select "Open with Live Server"

**Option C: Direct File Access**
1. Navigate to `frontend/pages/` folder
2. Double-click `index.html`
3. (May have CORS issues with some browsers)

### 7. Create Your First Account

1. Open the frontend in your browser
2. Click **Register**
3. Fill in:
   - Username
   - Email
   - Password (min 8 chars, 1 uppercase, 1 number)
   - Age
   - Gender
4. Click **Register**
5. You'll be automatically logged in

### 8. Test the System

**Test Text Analysis:**
1. In the chat interface, type: "I have a headache and fever"
2. Click Send
3. Wait for AI analysis (5-10 seconds)
4. Review the comprehensive disease analysis

**Test Image Upload:**
1. Click the attachment icon
2. Select an image file
3. Optionally add a message: "What is this?"
4. Click Send
5. AI will analyze the image and provide insights

**Test Export:**
1. After a few chats, click "Export" button
2. Choose format (PDF, DOCX, JSON, or CSV)
3. File will download automatically

**Test Comparison:**
1. Have at least 2 chat conversations
2. Select multiple chats (if UI supports it)
3. Click "Compare" to see symptom progression

## Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is already in use
# Windows:
netstat -ano | findstr :5000
# Mac/Linux:
lsof -i :5000

# If in use, kill the process or change port in app.py
```

### "Module not found" errors
```bash
# Make sure virtual environment is activated
# You should see (venv) in your terminal prompt

# Reinstall dependencies
pip install -r requirements.txt
```

### OpenAI API errors
- Verify your API key is correct in `.env`
- Check you have GPT-4 access enabled
- Ensure you have API credits available
- Check [status.openai.com](https://status.openai.com) for outages

### Supabase connection errors
- Verify SUPABASE_URL is correct
- Ensure you're using the **service_role** key, not anon key
- Check if schema.sql was executed successfully
- Verify your Supabase project is active

### File upload errors
- Check file size (max 16MB)
- Verify file type is supported
- Ensure `uploads` folder exists and has write permissions
- Check backend logs for specific errors

### Frontend can't connect to backend
- Verify backend is running on http://localhost:5000
- Check browser console for CORS errors
- Ensure `api.js` has correct API_BASE_URL
- Try using Python HTTP server instead of direct file access

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] Can register new account
- [ ] Can login with credentials
- [ ] Can send text message and get AI response
- [ ] Can upload image file
- [ ] Can upload video file
- [ ] Can view chat history
- [ ] Can export as PDF
- [ ] Can export as DOCX
- [ ] Can export as JSON
- [ ] Can export as CSV
- [ ] Can compare multiple chats
- [ ] Can delete individual chat
- [ ] Can update profile
- [ ] Can logout

## Next Steps

1. **Customize Symptoms Database**: Edit `backend/data/symptoms.json` to add more conditions
2. **Adjust AI Prompts**: Modify `backend/utils/ai_analyzer.py` for different analysis styles
3. **Customize UI**: Edit CSS files in `frontend/components/`
4. **Add More Features**: Extend routes in `backend/routes/`
5. **Deploy to Production**: See deployment guides for Heroku, AWS, or DigitalOcean

## Production Deployment Notes

Before deploying to production:

1. **Change JWT Secret**: Use a strong, random 32+ character secret
2. **Enable HTTPS**: Use SSL certificates (Let's Encrypt)
3. **Update CORS**: Restrict to your frontend domain only
4. **Set Environment**: Change `FLASK_ENV=production`
5. **Use Production Server**: Replace Flask dev server with Gunicorn/uWSGI
6. **Enable Rate Limiting**: Prevent API abuse
7. **Set Up Monitoring**: Use logging and error tracking
8. **Backup Database**: Regular Supabase backups
9. **Secure API Keys**: Use environment variables, never commit to git
10. **Review RLS Policies**: Ensure proper row-level security in Supabase

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review `API_DOCUMENTATION.md` for endpoint details
3. Check backend terminal for error messages
4. Check browser console for frontend errors
5. Verify all environment variables are set correctly

## Security Reminders

- Never commit `.env` file to version control
- Keep your OpenAI API key secret
- Use strong JWT secret in production
- Regularly update dependencies
- Monitor API usage and costs
- Implement rate limiting in production
- Use HTTPS in production

---

**You're all set! Start analyzing symptoms and building health awareness.** 🏥✨
