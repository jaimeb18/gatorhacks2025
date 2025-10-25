# Backend

This directory contains the backend services and API for the GatorHacks4 project.

## Overview

The backend handles server-side logic, database operations, API endpoints, and business logic.

## Getting Started

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```bash
   python app.py
   ```

## Project Structure

```
backend/
├── app.py              # Main application entry point
├── requirements.txt    # Python dependencies
├── models/             # Database models
├── routes/             # API route handlers
├── services/           # Business logic services
├── utils/              # Utility functions
└── tests/              # Backend tests
```

## API Documentation

API endpoints and documentation will be added here as the project develops.

## Environment Variables

Create a `.env` file in the backend directory with the following variables:
```
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
DEBUG=True
```

## Development

- Use Python 3.8+ for development
- Follow PEP 8 style guidelines
- Write tests for new features
- Use type hints for better code documentation
