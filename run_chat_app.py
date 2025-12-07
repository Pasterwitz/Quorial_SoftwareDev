#!/usr/bin/env python3
"""Simple script to run the Chat Flask application."""

import os
import sys

from dotenv import load_dotenv
import shutil

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_quorial import create_app

def main():
    # Load environment variables from .env if present so secrets can be stored in a file.
    load_dotenv()

    app = create_app()
    
    print("Starting Chat Application (database will not be reset automatically)...")
    print("Access the application at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
