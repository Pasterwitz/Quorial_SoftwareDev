#!/usr/bin/env python3
"""
Simple script to run the Chat Flask application
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_quorial import create_app

def main():
    app = create_app()
    
    # Initialize the database
    with app.app_context():
        from flask_quorial.db import init_db
        try:
            init_db()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    print("Starting Chat Application...")
    print("Access the application at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
