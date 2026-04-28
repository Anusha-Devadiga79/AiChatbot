# 🏥 AI-Driven Public Health Chatbot

A comprehensive full-stack web application for disease awareness using AI-powered symptom analysis with support for text, image, and video inputs.

## ✨ Key Features

### 🤖 Advanced AI Analysis
- **Multi-Modal Input Support**: Text, images, videos, and documents
- **Comprehensive Disease Analysis**: Disease identification, severity assessment, prevention, treatment options
- **Confidence Scoring**: AI confidence levels for each diagnosis
- **Differential Diagnosis**: Multiple possible conditions identified
- **Risk Factor Analysis**: Identifies contributing risk factors
- **Complication Warnings**: Alerts about potential complications

### 📊 Data Management
- **Chat History**: Complete conversation tracking with search
- **Comparison Analysis**: Compare multiple consultations to track symptom progression
- **Pattern Recognition**: Identify recurring conditions and severity changes
- **File Storage**: All uploaded files automatically stored and linked to chats

### 📤 Export Capabilities
- **PDF Export**: Formatted health reports with analysis details
- **DOCX Export**: Editable Word documents with tables
- **JSON Export**: Structured data for external analysis
- **CSV Export**: Spreadsheet-compatible format for data analysis
- **Selective Export**: Export all chats or specific consultations

### 🔒 Security & Privacy
- JWT Authentication
- User-specific data isolation
- Secure file uploads (16MB limit)
- Row-level security in database

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python (Flask)
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-4 with Vision API
- **Auth**: JWT (flask-jwt-extended)
- **Image Processing**: OpenCV, Pillow
- **Video Analysis**: OpenCV frame extraction
- **PDF Processing**: pdfplumber
- **Export**: reportlab (PDF), python-docx (DOCX)

## Project Structure
```
health-chatbot/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── requirements.txt
│   ├── .env.example            # Copy to .env and fill in values
│   ├── data/
│   │   └── symptoms.json       # WHO-based symptom dataset
│   ├── routes/
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── user_routes.py      # User profile management
│   │   ├── chat_routes.py      # Chat & analysis endpoints
│   │   ├── report_routes.py    # Medical report processing
│   │   ├── upload_routes.py    # File upload management
│   │   ├── export_routes.py    # Export functionality (PDF/DOCX/JSON/CSV)
│   │   └── admin_routes.py     # Admin panel endpoints
│   └── utils/
│       ├── db.py               # Supabase client
│       ├── auth_helpers.py     # Password hashing, validation
│       ├── ai_analyzer.py      # OpenAI GPT-4 integration
│       ├── chatbot.py          # Symptom matching engine
│       ├── pdf_extractor.py    # PDF text extraction
│       └── export_helper.py    # PDF/DOCX/JSON/CSV export generation
├── frontend/
│   ├── pages/
│   │   ├── index.html          # Login / Register
│   │   ├── dashboard.html      # Main user dashboard
│   │   └── admin.html          # Admin panel
│   └── components/
│       ├── styles.css          # Global styles
│       ├── auth.css            # Auth page styles
│       ├── dashboard.css       # Dashboard styles
│       ├── admin.css           # Admin styles
│       ├── api.js              # API client (all fetch calls)
│       ├── auth.js             # Login/register logic
│       ├── dashboard.js        # Dashboard logic
│       └── admin.js            # Admin logic
├── database/
│   └── schema.sql              # Supabase table definitions
├── uploads/                    # Local file storage (auto-created)
│   └── chat_files/             # Chat session uploads
├── API_DOCUMENTATION.md        # Comprehensive API documentation
└── README.md                   # This file
```

## Setup Instructions

### 1. Supabase Setup
1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run `database/schema.sql`
3. Copy your **Project URL** and **anon/service_role key** from Settings → API

### 2. OpenAI Setup
1. Get an API key from [platform.openai.com](https://platform.openai.com)
2. Ensure you have access to GPT-4 and GPT-4 Vision models

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your credentials (see below)

# Run the server
python app.py
```

### 4. Frontend Setup
Open `frontend/pages/index.html` in your browser, or serve with a local server:
```bash
# Using Python
python -m http.server 8080
# Then visit http://localhost:8080/frontend/pages/index.html
```

Or use VS Code Live Server extension.

## Environment Variables (.env)
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# JWT Configuration
JWT_SECRET_KEY=your-random-secret-key-here

# Flask Configuration
FLASK_ENV=development

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes

# Admin Configuration
ADMIN_EMAIL=admin@healthbot.com
```

## API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/auth/register | No | Register new user |
| POST | /api/auth/login | No | Login, returns JWT |

### User Management
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/user/get | Yes | Get user profile |
| PUT | /api/user/edit | Yes | Update profile |
| DELETE | /api/user/delete | Yes | Delete account |

### Chat & Analysis
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/chat/send | Yes | Send message/files, get AI analysis |
| GET | /api/chat/get | Yes | Get chat history with search |
| POST | /api/chat/compare | Yes | Compare multiple analyses |
| DELETE | /api/chat/delete/:id | Yes | Delete a chat |
| DELETE | /api/chat/delete-all | Yes | Delete all chats |

### Reports
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/report/upload | Yes | Upload PDF report |
| GET | /api/report/get | Yes | Get all reports |
| GET | /api/report/compare | Yes | Compare two reports |

### File Uploads
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/upload/create | Yes | Upload any file |
| GET | /api/upload/get | Yes | Get all uploads |
| DELETE | /api/upload/delete/:id | Yes | Delete upload |

### Export
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET/POST | /api/export/pdf | Yes | Export chats as PDF |
| GET/POST | /api/export/doc | Yes | Export chats as DOCX |
| GET/POST | /api/export/json | Yes | Export chats as JSON |
| GET/POST | /api/export/csv | Yes | Export chats as CSV |

### Admin
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/admin/stats | Admin | System statistics |
| GET | /api/admin/users | Admin | All users list |

## Usage Examples

### 1. Text-Based Symptom Analysis
```javascript
// Send symptoms via text
const response = await fetch('/api/chat/send', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: "I have a persistent cough, fever, and chest pain"
  })
});
```

### 2. Image Upload with Analysis
```javascript
// Upload image of rash or injury
const formData = new FormData();
formData.append('message', 'I have this rash on my arm');
formData.append('files', imageFile);

const response = await fetch('/api/chat/send', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### 3. Video Analysis
```javascript
// Upload video showing symptoms
const formData = new FormData();
formData.append('message', 'Video of my tremor');
formData.append('files', videoFile);

const response = await fetch('/api/chat/send', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### 4. Compare Multiple Consultations
```javascript
// Track symptom progression
const response = await fetch('/api/chat/compare', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    chat_ids: [1, 2, 3, 4]
  })
});
```

### 5. Export Health Report
```javascript
// Export specific chats as PDF
const response = await fetch('/api/export/pdf', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    chat_ids: [1, 2, 3]
  })
});

// Download the PDF
const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'health_report.pdf';
a.click();
```

## Supported File Types

### Images
- .jpg, .jpeg, .png, .gif, .webp
- Used for: Skin conditions, rashes, injuries, medical reports

### Videos
- .mp4, .avi, .mov, .mkv
- Used for: Movement disorders, breathing patterns, progressive symptoms

### Documents
- .pdf, .doc, .docx, .txt
- Used for: Medical reports, lab results, previous diagnoses

## AI Analysis Output

Each analysis provides:

1. **Disease Identification**: Primary condition name
2. **Description**: Detailed explanation (2-3 sentences)
3. **Symptoms**: List of common symptoms
4. **Severity**: mild/moderate/high classification
5. **Confidence Score**: 0-1 scale (displayed as percentage)
6. **Prevention**: Lifestyle changes and preventive measures
7. **Treatment Options**: General treatment approaches
8. **Home Remedies**: Safe self-care tips
9. **Risk Factors**: Conditions that increase risk
10. **Complications**: Potential issues if untreated
11. **When to See Doctor**: Specific warning signs
12. **Other Possible Conditions**: Differential diagnosis

## Comparison Analysis Features

When comparing multiple consultations:

- **Disease Tracking**: All conditions identified over time
- **Severity Progression**: Track if symptoms are worsening
- **Common Symptoms**: Most frequently reported symptoms
- **Date Range**: Time span of consultations
- **Recommendations**: AI-generated advice based on patterns
- **Summary**: Overview of health trends

## Export Formats

### PDF Export
- Professional formatting with color-coded sections
- Includes all analysis details
- User information and export timestamp
- Uploaded file references
- Page breaks for readability

### DOCX Export
- Editable Word document
- Structured tables for analysis data
- Easy to share with healthcare providers
- Compatible with all word processors

### JSON Export
- Complete structured data
- Ideal for external analysis tools
- Includes all metadata
- Machine-readable format

### CSV Export
- Spreadsheet-compatible
- Columns: Chat ID, Timestamp, Message, Disease, Severity, Confidence, Symptoms, etc.
- Easy to import into Excel, Google Sheets
- Great for data analysis and visualization

## Best Practices

1. **Detailed Descriptions**: Provide specific symptom details for better analysis
2. **Clear Images**: Use well-lit, focused images for accurate analysis
3. **Regular Tracking**: Use comparison feature to monitor symptom changes
4. **Export Regularly**: Keep personal health records updated
5. **File Organization**: Name files descriptively before uploading
6. **Privacy**: Never share exported reports containing personal health information
7. **Professional Consultation**: Always verify AI analysis with healthcare professionals

## Troubleshooting

### Backend Issues
```bash
# Check if Flask is running
curl http://localhost:5000/

# Check logs for errors
python app.py

# Verify environment variables
cat .env  # Linux/Mac
type .env  # Windows
```

### Database Issues
- Verify Supabase credentials in .env
- Check if schema.sql was executed
- Ensure RLS policies are configured

### OpenAI Issues
- Verify API key is valid
- Check API usage limits
- Ensure GPT-4 access is enabled

### File Upload Issues
- Check file size (max 16MB)
- Verify file type is supported
- Ensure uploads folder has write permissions

## Security Considerations

- All endpoints (except auth) require JWT authentication
- Passwords are hashed using bcrypt
- File uploads are validated for type and size
- User data is isolated (can only access own data)
- SQL injection protection via Supabase client
- CORS configured for frontend origin

## Performance Optimization

- Database indexes on user_id and timestamp
- Pagination for chat history (20 items per page)
- File size limits to prevent server overload
- Efficient video frame extraction (5 frames max)
- Image compression for storage optimization

## Future Enhancements

- [ ] Real-time chat with WebSocket support
- [ ] Voice input for symptom description
- [ ] Multi-language support
- [ ] Integration with wearable devices
- [ ] Appointment scheduling with doctors
- [ ] Medication reminders
- [ ] Health metrics tracking (blood pressure, glucose, etc.)
- [ ] Community health forums
- [ ] Telemedicine integration

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and awareness purposes only.

## Disclaimer

⚠️ **IMPORTANT MEDICAL DISCLAIMER**

This application is for **awareness and educational purposes only**. It is NOT a substitute for professional medical advice, diagnosis, or treatment.

- Always consult a qualified healthcare professional for medical concerns
- Never disregard professional medical advice based on information from this app
- In case of emergency, call your local emergency services immediately
- The AI analysis is based on patterns and may not be accurate for your specific situation
- This tool does not replace physical examination, laboratory tests, or imaging studies

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check API_DOCUMENTATION.md for detailed endpoint information
- Review troubleshooting section above

## Acknowledgments

- OpenAI for GPT-4 and Vision API
- Supabase for database and authentication infrastructure
- WHO for symptom and disease information
- Open-source community for libraries and tools

---

**Built with ❤️ for public health awareness**
