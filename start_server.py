#!/usr/bin/env python3
"""
GatorHacks4 File Upload Server
Run this script to start the file upload web application
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting GatorHacks4 File Upload Server...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend/app.py'):
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected to find: backend/app.py")
        sys.exit(1)
    
    # Check if Flask is installed
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask not found. Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'Flask', 'Werkzeug'])
    
    # Change to backend directory and start the server
    os.chdir('backend')
    
    print("\n📁 Upload folder will be created at:", os.path.abspath('uploads'))
    print("🌐 Access the upload page at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    try:
        import app
        app.app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
