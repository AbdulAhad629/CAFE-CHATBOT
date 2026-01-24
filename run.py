"""
Main entry point for the WhatsApp Cafeteria Chatbot
Run this file to start the Flask application
"""
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from app import create_app
import os

# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.getenv('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
