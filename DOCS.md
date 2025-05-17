# FilePipeline Documentation

## Overview

FilePipeline is a Django application designed to process legal documents using AI. The system extracts information from legal texts and generates appropriate responses through an API-driven architecture.

## Quick Start Guide

### Installation

1. Clone the repository
2. Set up a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

```bash
cd webserv
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## Features

- **Document Processing**: Upload and process legal documents
- **AI-Powered Analysis**: Generate responses to legal claims
- **Template System**: Use templates with placeholders for document generation
- **API Interface**: Programmatically interact with the system

## API Reference

### Placeholder Values Endpoint

`POST /placeholder_values/`

Processes legal text and returns AI-generated values for template placeholders.

#### Request Format

```json
{
  "file_text": "Full text of legal document to analyze",
  "template_text": "Optional template with ${placeholders}",
  "placeholder_regex": "Optional custom regex pattern",
  "mock": false
}
```

#### Response Format

```json
{
  "placeholder_values": ["Response 1", "Response 2", "..."],
  "original_text": "Original document content",
  "prompt": {
    "system_prompt": "AI system prompt used",
    "user_prompt": "AI user prompt used"
  }
}
```

### Upload File Endpoint

`POST /upload/`

Handles document uploads for processing.

#### Request Format

- Method: POST
- Form Data:
  - file: The document file to upload (PDF or DOCX)

#### Response Format

- Success: Redirects to `/send_file/`
- Error: HTML response with error message

### Send File Endpoint

`GET /send_file/`

Processes the most recently uploaded file, converts it if necessary, and generates a response document.

#### Request Format

- Method: GET
- No parameters required

#### Response Format

- Success: HTML page with download link to the generated document
- Error: HTML response with error message

### Download File Endpoint

`GET /download/<filename>`

Downloads a specific file from the media directory.

#### Request Format

- Method: GET
- URL Parameter:
  - filename: Name of the file to download

#### Response Format

- Success: File download response
- Error: 404 Not Found

### Home Endpoint

`GET /`

Displays the main application homepage.

#### Request Format

- Method: GET
- No parameters required

#### Response Format

- HTML page for the application's main interface

## Technical Architecture

The application follows a modular design:

- **Views Layer**: Handles HTTP requests/responses
- **Service Layer**: Contains business logic and AI integration
- **Parsing Layer**: Extracts information from documents
- **Template Layer**: Manages document generation

## Development Guidelines

- Follow PEP 8 standards for Python code
- Document new API endpoints
- Write tests for new features
- Use Django's ORM for database operations

## Troubleshooting

- **Server won't start**: Check if port 8000 is already in use
- **API errors**: Verify JSON formatting in requests
- **File processing issues**: Ensure uploaded files are in supported formats

## License

This project is proprietary and confidential.
