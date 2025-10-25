# GatorHacks4 Project

This is a project for GatorHacks4 hackathon featuring a modern file upload web application.

## Project Structure

- `backend/` - Flask backend with file upload API
- `frontend/` - Modern HTML/CSS/JS upload interface
- `prompts/` - AI prompts and templates
- `src/` - Source code with main.py entry point

## Features

✨ **File Upload Web App**
- Drag & drop file upload interface
- Multiple file selection
- Real-time upload progress
- File type validation
- Responsive design
- Secure file handling

## Getting Started

### Quick Start
1. Clone the repository
2. Set up Google Cloud Vision API credentials:
   - Copy `backend/service-account-key.json.example` to `backend/service-account-key.json`
   - Replace the placeholder values with your actual Google Cloud service account credentials
3. Run the file upload server:
   ```bash
   python start_server.py
   ```
4. Open http://localhost:5000 in your browser

### Manual Setup
1. Install Python dependencies:
   ```bash
   pip install Flask Werkzeug
   ```
2. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```
3. Access the upload page at http://localhost:5000

## Development

### Backend API Endpoints
- `GET /` - Serve upload page
- `POST /upload` - Handle file uploads
- `GET /files` - List uploaded files
- `GET /download/<filename>` - Download files

### Frontend Features
- Modern drag & drop interface
- File preview and management
- Upload progress tracking
- Error handling and validation

## File Upload Limits
- Maximum file size: 16MB
- Allowed file types: txt, pdf, png, jpg, jpeg, gif, doc, docx, xls, xlsx, zip, rar
- Files are stored securely with unique names
