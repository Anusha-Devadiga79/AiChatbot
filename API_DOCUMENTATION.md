# AI Public Health Chatbot - API Documentation

## Overview
This API provides comprehensive symptom analysis with support for text, image, and video inputs. It includes features for disease identification, severity assessment, export functionality, and comparison analysis.

## Base URL
```
http://localhost:5000/api
```

## Authentication
All endpoints (except auth endpoints) require JWT authentication.
Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Chat Endpoints

### 1. Send Message with Symptom Analysis
**POST** `/chat/send`

Analyze symptoms provided via text, image, or video. Supports multiple file uploads.

**Content-Type:** `multipart/form-data` or `application/json`

**Request (Multipart Form):**
```
message: "I have a headache and fever" (optional if files provided)
files: [file1, file2, ...] (optional, supports images/videos/PDFs)
```

**Request (JSON):**
```json
{
  "message": "I have a headache and fever"
}
```

**Response:**
```json
{
  "chat_id": 123,
  "message": "I have a headache and fever",
  "response": "Formatted analysis response",
  "analysis": {
    "matched": true,
    "disease": "Common Cold",
    "description": "Viral infection affecting upper respiratory tract",
    "symptoms": ["headache", "fever", "runny nose"],
    "prevention": "Wash hands frequently, avoid close contact...",
    "severity": "mild",
    "when_to_see_doctor": "If fever exceeds 103°F or lasts more than 3 days",
    "other_possible_conditions": ["Flu", "Sinusitis"],
    "confidence": 0.85,
    "risk_factors": ["Weakened immune system", "Close contact with infected"],
    "complications": "Can lead to secondary bacterial infections",
    "treatment_options": "Rest, fluids, over-the-counter medications",
    "home_remedies": "Drink warm liquids, use humidifier, get adequate rest",
    "disclaimer": "⚠️ This is for awareness purposes only..."
  },
  "uploaded_files": ["uploads/chat_files/1_20260428_image.jpg"],
  "timestamp": "2026-04-28T10:30:00"
}
```

**Supported File Types:**
- Images: .jpg, .jpeg, .png, .gif, .webp
- Videos: .mp4, .avi, .mov, .mkv
- Documents: .pdf, .doc, .docx, .txt

---

### 2. Get Chat History
**GET** `/chat/get`

Retrieve user's chat history with optional search and pagination.

**Query Parameters:**
- `search` (optional): Search term to filter messages
- `page` (optional, default: 1): Page number
- `limit` (optional, default: 20): Items per page

**Response:**
```json
{
  "chats": [
    {
      "chat_id": 123,
      "user_id": 1,
      "message": "I have a headache",
      "response": "Analysis response...",
      "analysis": {...},
      "uploaded_files": "uploads/chat_files/file.jpg",
      "timestamp": "2026-04-28T10:30:00"
    }
  ],
  "page": 1,
  "limit": 20
}
```

---

### 3. Compare Multiple Analyses
**POST** `/chat/compare`

Compare multiple chat analyses to identify patterns, severity progression, and recurring conditions.

**Request:**
```json
{
  "chat_ids": [123, 124, 125]
}
```

**Response:**
```json
{
  "total_chats": 3,
  "date_range": {
    "first": "2026-04-20T10:00:00",
    "last": "2026-04-28T10:30:00"
  },
  "diseases_identified": [
    {
      "chat_id": 123,
      "timestamp": "2026-04-20T10:00:00",
      "disease": "Common Cold",
      "severity": "mild",
      "confidence": 0.85
    }
  ],
  "severity_progression": [
    {
      "chat_id": 123,
      "timestamp": "2026-04-20T10:00:00",
      "severity": "mild"
    }
  ],
  "common_symptoms": [
    {
      "symptom": "headache",
      "frequency": 3
    },
    {
      "symptom": "fever",
      "frequency": 2
    }
  ],
  "recommendations": [
    "📊 Severity levels are changing. Monitor symptoms closely.",
    "🔄 Recurring condition detected. Follow-up with healthcare provider advised."
  ],
  "summary": "Analyzed 3 consultations from 2026-04-20 to 2026-04-28. Identified 2 unique condition(s)."
}
```

---

### 4. Delete Chat
**DELETE** `/chat/delete/<chat_id>`

Delete a specific chat by ID.

**Response:**
```json
{
  "message": "Chat deleted"
}
```

---

### 5. Delete All Chats
**DELETE** `/chat/delete-all`

Delete all chats for the authenticated user.

**Response:**
```json
{
  "message": "All chats deleted"
}
```

---

## Export Endpoints

All export endpoints support both GET (export all) and POST (export specific chats).

### 1. Export as PDF
**GET/POST** `/export/pdf`

Export chat history as a formatted PDF document.

**POST Request (optional):**
```json
{
  "chat_ids": [123, 124, 125]
}
```

**Response:** PDF file download

---

### 2. Export as DOCX
**GET/POST** `/export/doc`

Export chat history as a Word document.

**POST Request (optional):**
```json
{
  "chat_ids": [123, 124, 125]
}
```

**Response:** DOCX file download

---

### 3. Export as JSON
**GET/POST** `/export/json`

Export chat history as structured JSON data.

**POST Request (optional):**
```json
{
  "chat_ids": [123, 124, 125]
}
```

**Response:** JSON file download
```json
{
  "user": {
    "username": "john_doe",
    "email": "john@example.com"
  },
  "exported_at": "2026-04-28T10:30:00",
  "total_chats": 10,
  "chats": [...]
}
```

---

### 4. Export as CSV
**GET/POST** `/export/csv`

Export chat history as CSV for data analysis.

**POST Request (optional):**
```json
{
  "chat_ids": [123, 124, 125]
}
```

**Response:** CSV file download with columns:
- Chat ID
- Timestamp
- User Message
- Disease
- Severity
- Confidence
- Symptoms
- Prevention
- When to See Doctor
- Uploaded Files
- Response

---

## Upload Endpoints

### 1. Upload File
**POST** `/upload/create`

Upload a file (image, video, or document) for analysis.

**Content-Type:** `multipart/form-data`

**Request:**
```
file: <file_data>
```

**Response:**
```json
{
  "message": "File uploaded successfully",
  "upload_id": 456,
  "file_path": "uploads/image/1_20260428_photo.jpg",
  "file_type": "image"
}
```

---

### 2. Get Uploads
**GET** `/upload/get`

Retrieve user's uploaded files.

**Query Parameters:**
- `type` (optional): Filter by file type (image/video/document)

**Response:**
```json
{
  "uploads": [
    {
      "upload_id": 456,
      "user_id": 1,
      "file_path": "uploads/image/1_20260428_photo.jpg",
      "file_type": "image",
      "created_at": "2026-04-28T10:30:00"
    }
  ]
}
```

---

### 3. Delete Upload
**DELETE** `/upload/delete/<upload_id>`

Delete an uploaded file.

**Response:**
```json
{
  "message": "Upload deleted"
}
```

---

## Analysis Features

### Comprehensive Disease Analysis
The AI analyzer provides:

1. **Disease Identification**: Primary condition matching
2. **Description**: Detailed explanation of the condition
3. **Symptoms**: List of common symptoms
4. **Severity Assessment**: mild/moderate/high classification
5. **Confidence Score**: 0-1 scale indicating analysis confidence
6. **Prevention**: Lifestyle changes and preventive measures
7. **Treatment Options**: General treatment approaches
8. **Home Remedies**: Safe self-care tips
9. **Risk Factors**: Conditions that increase risk
10. **Complications**: Potential issues if untreated
11. **When to See Doctor**: Specific warning signs
12. **Differential Diagnosis**: Other possible conditions

### Multi-Modal Input Support

**Text Input:**
- Natural language symptom descriptions
- Medical history information

**Image Input:**
- Skin conditions, rashes, injuries
- Medical reports, test results
- Visual symptoms

**Video Input:**
- Movement disorders, tremors
- Breathing patterns
- Progressive symptoms

**Document Input:**
- PDF medical reports
- Lab results
- Previous diagnoses

---

## File Storage

All uploaded files during chat sessions are automatically stored in:
```
uploads/chat_files/
```

File naming convention:
```
{user_id}_{timestamp}_{original_filename}
```

Files are linked to chat records and included in exports.

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

---

## Usage Examples

### Example 1: Text-based Symptom Analysis
```bash
curl -X POST http://localhost:5000/api/chat/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a persistent cough and chest pain"}'
```

### Example 2: Image Upload with Symptoms
```bash
curl -X POST http://localhost:5000/api/chat/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "message=I have this rash on my arm" \
  -F "files=@rash_photo.jpg"
```

### Example 3: Compare Multiple Consultations
```bash
curl -X POST http://localhost:5000/api/chat/compare \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"chat_ids": [1, 2, 3]}'
```

### Example 4: Export Specific Chats as PDF
```bash
curl -X POST http://localhost:5000/api/export/pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"chat_ids": [1, 2, 3]}' \
  --output health_report.pdf
```

---

## Best Practices

1. **File Size**: Keep uploads under 16MB
2. **Image Quality**: Use clear, well-lit images for better analysis
3. **Symptom Description**: Be specific and detailed
4. **Regular Exports**: Export data regularly for personal health records
5. **Comparison Analysis**: Use comparison feature to track symptom progression
6. **Privacy**: All data is user-specific and secured with JWT authentication

---

## Disclaimer

This API provides health awareness information only. All analyses should be verified by qualified healthcare professionals. Never use this as a substitute for professional medical advice, diagnosis, or treatment.
