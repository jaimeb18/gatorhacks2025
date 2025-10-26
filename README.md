# TravelBuddy AI

An intelligent web application that uses AI to recognize and analyze artwork, food, and architecture from uploaded images, providing detailed information, historical context, and personalized recommendations.

## Project Overview

TravelBuddy AI is a hackathon project for GatorHacks4 that combines Google Cloud Vision API, Google's Gemini AI model, and Google Places API to create an interactive image recognition and analysis platform. Upload images of artwork, food, or architecture and receive instant AI-powered insights, historical context, and location-based recommendations.

## Features

### AI-Powered Recognition
- **Artwork Analysis**: Identify famous paintings and sculptures with artist information, year created, and museum locations
- **Food Recognition**: Detect dishes and cuisines with detailed descriptions and ingredient information
- **Architecture Analysis**: Identify buildings and structures with historical context and architectural details

### Smart Recommendations
- **Art Suggestions**: Discover similar artworks in the same city or country
- **Restaurant Suggestions**: Find places to enjoy the same cuisine near you (New York)
- **Architecture Suggestions**: Explore similar buildings with Wikipedia and Google Maps links

### Detailed Insights
- AI-generated descriptions and historical context
- Wikipedia links for deeper learning
- Google Maps integration for restaurant locations
- Theme-based suggestions

## Project Structure

```
gatorhacks4/
├── backend/
│   ├── app.py                    # Flask backend server
│   ├── agent.py                  # AI agent for LLM interactions
│   ├── config.py                 # API keys configuration
│   ├── requirements.txt          # Python dependencies
│   ├── Prompts/                  # AI prompt templates
│   │   ├── Artworks_*.txt
│   │   ├── Food_*.txt
│   │   └── Architecture_*.txt
│   └── uploads/                  # Image storage (temp)
├── frontend/
│   ├── index.html                # Homepage
│   ├── art.html                  # Art recognition page
│   ├── food.html                 # Food recognition page
│   ├── architecture.html          # Architecture page
│   ├── styles.css                # Global styles
│   ├── script.js                 # Art page JS
│   ├── food.js                   # Food page JS
│   └── architecture.js           # Architecture page JS
└── README.md
```

## Tech Stack

### Backend
- **Python 3.x**
- **Flask 2.3.3** - Web framework
- **Google Cloud Vision API** - Image recognition and analysis
- **Google Gemini AI (gemini-2.5-flash)** - LLM for descriptions and suggestions
- **Google Places API** - Restaurant and location data
- **Werkzeug** - WSGI utilities

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with responsive design
- **Vanilla JavaScript** - Client-side functionality
- **Mobile-responsive** - Works on desktop, tablet, and mobile devices

## Getting Started

### Prerequisites
- Python 3.7+
- Google Cloud account with Vision API enabled
- Google Generative AI API key
- Google Places API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jaimeb18/gatorhacks2025.git
   cd gatorhacks4
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   - Update `backend/config.py` with your Google API keys
   - Place your `service-account-key.json` in the `backend/` directory for Google Cloud Vision

4. **Start the Flask server**
   ```bash
   cd backend
   python app.py
   ```

5. **Access the application**
   - Desktop: Open http://localhost:5000
   - Mobile: Use your local IP address (e.g., http://10.136.89.219:5000)

## API Endpoints

### Art Recognition
- `GET /art` - Art recognition page
- `POST /upload` - Upload and analyze artwork images
- `GET /get_themes/<artwork_name>` - Get artwork themes
- `GET /get_suggestions/<artwork_name>` - Get similar artwork suggestions

### Food Recognition
- `GET /food` - Food recognition page
- `POST /upload_food` - Upload and analyze food images
- `GET /get_food_details/<food_name>` - Get food descriptions
- `GET /get_food_suggestions/<food_name>?location=<city>` - Get restaurant suggestions

### Architecture Recognition
- `GET /architecture` - Architecture page
- `POST /upload_architecture` - Upload and analyze building images
- `GET /get_architecture_details/<building_name>` - Get building descriptions
- `GET /get_architecture_suggestions/<building_name>` - Get similar architecture suggestions

## Features in Detail

### Image Recognition
- Uses Google Cloud Vision API for accurate image analysis
- Detects famous artworks, food dishes, and architectural landmarks
- Provides confidence scores for identification accuracy

### AI-Powered Analysis
- **Gemini 2.5 Flash** generates detailed descriptions
- Historical context and cultural significance
- Wikipedia links for additional information
- Themed suggestions based on extracted characteristics

### Interactive Recommendations
- **Art**: Find 6 similar artworks with locations
- **Food**: Get restaurant suggestions in your area
- **Architecture**: Discover related buildings with maps links

### Mobile-First Design
- Fully responsive layout
- Touch-friendly upload interface
- Optimized for mobile browsing

## Team

- **Jaime Breitkreutz** - Data Science Major
- **Yimo Liu** - Data Science + Economics Major
- **Max Hyken** - Computer Engineering Major

## Notes

- Maximum file size: 16MB
- Supported formats: JPG, PNG, GIF
- Images are temporarily stored (last 20 images)
- All analysis results are generated in real-time via AI

## Security

- Secure file upload handling with UUIDs
- API keys stored in configuration file (not in repo)
- Input validation and sanitization
- Temporary file cleanup

## License

This project was created for GatorHacks4 hackathon.
