# TellATale MVP - Repository Guide

## Overview

TellATale MVP is a simple web application designed to generate stories based on user prompts. Currently in its MVP stage, the application uses a Flask backend with HTML/CSS/JavaScript frontend. It provides a placeholder for AI-generated stories that will be integrated with Gemini AI in the future.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple client-server architecture:

1. **Frontend**: HTML/CSS/JavaScript for the user interface
2. **Backend**: Python Flask application serving the frontend and handling API requests
3. **Future Integration**: Placeholder for Gemini AI integration for story generation

The application is structured to serve a simple web interface where users can input story prompts, and the backend processes these requests to generate stories.

## Key Components

### Backend

- **Flask Application** (`main.py`): The core of the backend that handles HTTP requests, serves the frontend, and processes story generation requests.
- **Placeholder Story Generator**: A function (`get_story_from_ai`) that currently returns a dummy response but will later be replaced with actual AI integration.

### Frontend

- **HTML Interface** (`templates/index.html`): The main user interface containing:
  - A textarea for users to input story prompts
  - A "Generate Tale" button
  - A display area for the generated story
- **CSS Styling** (`static/style.css`): Minimal styling to make the application usable and visually appealing.
- **JavaScript Logic** (`static/script.js`): Handles the interaction between the frontend and backend:
  - Captures user input
  - Sends requests to the backend
  - Updates the UI with the generated story

## Data Flow

1. User enters a story prompt in the textarea and clicks "Generate Tale" (or presses Enter)
2. JavaScript captures the input and sends a POST request to `/generate_tale` endpoint
3. The Flask backend receives the request and processes it:
   - Extracts the prompt text
   - Calls the placeholder `get_story_from_ai` function
   - Returns the generated story as a JSON response
4. JavaScript updates the UI to display the generated story

## External Dependencies

The application relies on the following external dependencies:

- **Flask**: Web framework for the backend
- **Bootstrap CSS** (loaded from CDN): Frontend styling framework using the Replit dark theme
- **Gunicorn**: WSGI HTTP server for production deployment
- **PostgreSQL**: Database system (configured but not currently used)
- **Additional Python packages**:
  - flask-sqlalchemy (for future database integration)
  - email-validator
  - psycopg2-binary (PostgreSQL adapter)

## Deployment Strategy

The application is configured to deploy on Replit with the following settings:

- **Runtime Environment**: Python 3.11
- **Deployment Target**: Autoscale
- **Run Command**: `gunicorn --bind 0.0.0.0:5000 main:app`
- **Dependencies**: OpenSSL and PostgreSQL packages are included in the Nix configuration
- **Workflows**: 
  - "Project" workflow runs the application
  - "Start application" workflow executes gunicorn with hot reloading for development

## Development Guidelines

1. **Backend Enhancements**:
   - Complete the implementation of the `get_story_from_ai` function to integrate with Gemini AI
   - Add proper error handling for the API integration
   - Consider adding a database to store user prompts and generated stories

2. **Frontend Improvements**:
   - Complete the JavaScript implementation for handling API responses
   - Add additional UI features like saving stories or sharing options
   - Enhance the styling for a better user experience

3. **Database Integration**:
   - The project includes SQLAlchemy and PostgreSQL dependencies, suggesting future database integration
   - Consider implementing a database schema for storing user data, prompts, and generated stories

## Future Considerations

1. **User Authentication**: Add login functionality to allow users to save their stories
2. **Story Customization**: Provide additional options for story customization (length, style, genre)
3. **Performance Optimization**: Implement caching for frequently requested story types
4. **Mobile Responsiveness**: Enhance mobile experience with responsive design improvements