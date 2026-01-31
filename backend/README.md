# MLJ Results Compiler - Node.js Backend

Complete backend system for processing Excel test results and generating compiled output files.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ (download from nodejs.org)
- npm (comes with Node.js)

### Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

Server will start on `http://localhost:3000`

## 📋 API Endpoints

### 1. Upload Excel Files
**Endpoint:** `POST /api/upload`

Upload 5 Excel test result files (TEST_1.xlsx through TEST_5.xlsx)

**Request:**
- Content-Type: multipart/form-data
- Body: Files field with up to 5 .xlsx files

**Response:**
```json
{
  "success": true,
  "uploadedCount": 5,
  "totalSize": 1024000,
  "totalSizeMB": "1.00",
  "files": [
    {
      "originalName": "TEST_1.xlsx",
      "storedName": "uuid-filename.xlsx",
      "size": 204800,
      "rowCount": 100
    }
  ],
  "status": "ready_for_processing",
  "timestamp": "2026-01-31T12:00:00.000Z"
}
```

### 2. Process Files
**Endpoint:** `POST /api/process`

Process uploaded files to generate results

**Request:**
```json
{
  "files": [
    "uuid1-filename.xlsx",
    "uuid2-filename.xlsx",
    "uuid3-filename.xlsx",
    "uuid4-filename.xlsx",
    "uuid5-filename.xlsx"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "jobId": "job_1675123456_abc123def",
  "status": "processing",
  "message": "Processing started",
  "timestamp": "2026-01-31T12:00:00.000Z"
}
```

### 3. Check Processing Status
**Endpoint:** `GET /api/process-status/:jobId`

Check the status of a processing job

**Response:**
```json
{
  "success": true,
  "job": {
    "id": "job_1675123456_abc123def",
    "status": "complete",
    "startedAt": "2026-01-31T12:00:00.000Z",
    "completedAt": "2026-01-31T12:00:30.000Z",
    "participantCount": 115,
    "passCount": 95,
    "failCount": 20,
    "error": null
  },
  "timestamp": "2026-01-31T12:00:30.000Z"
}
```

### 4. Download Results
**Endpoint:** `GET /api/download/:jobId`

Download the generated result Excel file

**Response:** Excel file as attachment

**Headers:**
- Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- Content-Disposition: attachment; filename="Results_2026-01-31.xlsx"

### 5. Get Processing History
**Endpoint:** `GET /api/history?limit=50`

Get list of all processing jobs (default 50, max 100)

**Response:**
```json
{
  "success": true,
  "totalJobs": 5,
  "jobs": [
    {
      "id": "job_1675123456_abc123def",
      "status": "complete",
      "uploadedAt": "2026-01-31T12:00:00.000Z",
      "processedAt": "2026-01-31T12:00:30.000Z",
      "inputFiles": ["TEST_1.xlsx", "TEST_2.xlsx", ...],
      "participantCount": 115,
      "passCount": 95,
      "failCount": 20,
      "error": null
    }
  ],
  "timestamp": "2026-01-31T12:00:30.000Z"
}
```

### 6. Health Check
**Endpoint:** `GET /health`

Check if backend is running

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-31T12:00:00.000Z"
}
```

## 📁 Project Structure

```
backend/
├── src/
│   ├── server.js                 # Main Express server
│   ├── routes/
│   │   ├── upload.js            # File upload endpoint
│   │   ├── process.js           # Processing endpoint
│   │   ├── download.js          # Download endpoint
│   │   └── history.js           # History endpoint
│   ├── utils/
│   │   ├── validators.js        # File validation functions
│   │   └── excelProcessor.js    # Excel processing logic
│   └── middleware/
│       ├── requestLogger.js     # Request logging
│       └── errorHandler.js      # Global error handling
├── uploads/                      # Temporary file storage
├── package.json
├── .env.example
└── RENDER_DEPLOYMENT.md
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file based on `.env.example`:

```
NODE_ENV=development
PORT=3000
CORS_ORIGIN=http://localhost:3000,https://mljresultscompiler.vercel.app
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
```

**Variables:**
- `NODE_ENV`: Set to 'development' or 'production'
- `PORT`: Server port (default 3000)
- `CORS_ORIGIN`: Comma-separated list of allowed origins
- `MAX_FILE_SIZE`: Maximum file size in bytes (10MB = 10485760)
- `UPLOAD_DIR`: Directory for temporary file storage

## 🔄 Processing Flow

```
1. User uploads 5 Excel files
   ↓
2. Files validated (format, structure, columns)
   ↓
3. Files stored in uploads/ with UUID names
   ↓
4. User initiates processing
   ↓
5. Backend reads all 5 files
   ↓
6. Data merged on participant name
   ↓
7. Scores calculated using formula:
   SCORE = (TEST_1 + TEST_2 + TEST_3 + TEST_4 + TEST_5 + 0.8) × 16.6666
   ↓
8. STATUS assigned: PASS if SCORE >= 50, else FAIL
   ↓
9. New Excel file generated with results
   ↓
10. User downloads result file
```

## 📊 Excel Processing Details

### Input Format
Each Excel file must have:
- Sheet named "Responses" or first sheet will be used
- Columns: "Full Names", "Email", "Result"
- Result should be numeric (test score)

### Output Format
Generated Excel file includes:
- Columns: S/N, Full Names, Email, TEST_1, TEST_2, TEST_3, TEST_4, TEST_5, SCORE, STATUS
- All numeric scores formatted
- Headers in bold
- Auto-fitted column widths

### Processing Formula
```
TOTAL = TEST_1 + TEST_2 + TEST_3 + TEST_4 + TEST_5
SCORE = (TOTAL + 0.8) × 16.6666
STATUS = IF(SCORE >= 50, "PASS", "FAIL")
```

## 🧪 Testing

### Test Locally

1. Start backend:
```bash
npm run dev
```

2. Upload files using curl:
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "files=@TEST_1.xlsx" \
  -F "files=@TEST_2.xlsx" \
  -F "files=@TEST_3.xlsx" \
  -F "files=@TEST_4.xlsx" \
  -F "files=@TEST_5.xlsx"
```

3. Process files:
```bash
curl -X POST http://localhost:3000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["uuid1.xlsx", "uuid2.xlsx", "uuid3.xlsx", "uuid4.xlsx", "uuid5.xlsx"]
  }'
```

4. Check status:
```bash
curl http://localhost:3000/api/process-status/job_12345_abc
```

5. Download results:
```bash
curl http://localhost:3000/api/download/job_12345_abc -o Results.xlsx
```

6. View history:
```bash
curl http://localhost:3000/api/history
```

## 🚀 Deployment

### Deploy to Render.com (Recommended)

1. Follow instructions in `RENDER_DEPLOYMENT.md`
2. Key steps:
   - Create Render.com account
   - Connect GitHub repository
   - Set environment variables
   - Deploy

### Deploy to Railway.app

Similar process to Render.com - both platforms support Node.js

### Deploy to Heroku

Heroku free tier is deprecated, but paid plans available starting at $7/month

## 🔐 Security Considerations

- File uploads validated (format and size)
- CORS configured to specific domains
- Environment variables used for secrets
- Error messages don't expose internal details
- Files auto-deleted after 7 days (in production)

## 📝 Logs

Backend logs all operations for debugging:

```
→ 2026-01-31T12:00:00Z | POST /api/upload
  Query: {}
← 200 | 1250ms

→ 2026-01-31T12:00:01Z | POST /api/process
  Query: {}
← 202 | 50ms

[Processing in background...]
✅ Processing complete - 115 participants, 95 PASS, 20 FAIL
```

## ❌ Error Handling

All errors return JSON with helpful messages:

```json
{
  "error": true,
  "message": "File must be Excel format (.xlsx)",
  "status": 400,
  "timestamp": "2026-01-31T12:00:00.000Z"
}
```

Common errors:
- **400**: Bad request (invalid file, missing fields)
- **404**: Not found (job not found, file not found)
- **500**: Server error (processing failed, internal error)

## 📚 Dependencies

- **express**: Web framework
- **cors**: Cross-origin request handling
- **multer**: File upload handling
- **xlsx**: Excel file reading/writing
- **uuid**: Unique file identifiers
- **dotenv**: Environment variable loading

## 📞 Support

For issues or questions:
1. Check error messages in logs
2. Review `.copilot-directives.md` for detailed requirements
3. Check CORS configuration if frontend can't reach backend
4. Verify file format is valid Excel (.xlsx)

## 📄 License

ISC

---

**Status**: Production Ready  
**Last Updated**: January 31, 2026
