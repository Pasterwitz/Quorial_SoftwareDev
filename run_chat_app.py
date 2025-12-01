#!/usr/bin/env python3
"""
Simple script to run the Chat Flask application
"""

import os
import sys
import shutil

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_quorial import create_app

def main():
    app = create_app()
    
    # Initialize the database
    with app.app_context():
        from flask_quorial.db import init_db
        try:
            # Allow forcing a reset in development via environment var.
            # If RESET_DB is truthy (1/true/yes) the existing DB file will
            # be backed up and removed before initialization.
            db_path = app.config.get('DATABASE')
            reset_db = os.environ.get('RESET_DB')
            if reset_db and str(reset_db).lower() in ('1', 'true', 'yes'):
                if db_path and os.path.exists(db_path):
                    bak_path = db_path + '.bak'
                    try:
                        shutil.copy2(db_path, bak_path)
                        os.remove(db_path)
                        print(f"RESET_DB=1: backed up {db_path} to {bak_path} and removed the original")
                    except Exception as e:
                        print(f"RESET_DB backup/remove error: {e}")
                init_db()
                print("Database initialized successfully (forced by RESET_DB).")
            else:
                # Only initialize the DB if it does not already exist. The original
                # behavior always re-ran the schema and data scripts on every start,
                # which dropped existing tables and removed any registered users.
                if db_path is None or not os.path.exists(db_path):
                    init_db()
                    print("Database initialized successfully!")
                else:
                    print(f"Database already exists at {db_path}; skipping init.")
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    print("Starting Chat Application...")
    print("Access the application at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
