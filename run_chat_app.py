#!/usr/bin/env python3
"""Simple script to run the Chat Flask application."""

from logging import debug
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
    
    certificate_path = os.environ.get("CERTIFICATE_PATH")
    if certificate_path:
        
        print(f"Using SSL certificates from {certificate_path}")
        
        app.run(ssl_context=(os.path.join(certificate_path, 'fullchain1.pem'), os.path.join(certificate_path, 'privkey1.pem')), debug=True, host='0.0.0.0', port=443)
    else:
        app.run(debug=True, host='127.0.0.1', port=5000)
    
    

if __name__ == '__main__':
    
    main()
    
