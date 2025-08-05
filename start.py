#!/usr/bin/env python3
"""
NEET College Predictor - Startup Script
This script trains the model and starts the Flask application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import cv2
        import numpy
        import pandas
        import sklearn
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def train_model():
    """Train the college prediction model"""
    print("\n📊 Training college prediction model...")
    try:
        result = subprocess.run([sys.executable, "train_model.py"], 
                              capture_output=True, text=True, check=True)
        print("✅ Model training completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Model training failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Directories created")

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting NEET College Predictor...")
    print("📱 Application will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main startup function"""
    print("🎓 NEET College Predictor")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create directories
    create_directories()
    
    # Train model if it doesn't exist
    if not os.path.exists('college_model.pkl'):
        if not train_model():
            return
    else:
        print("✅ Model already exists, skipping training")
    
    # Start application
    start_application()

if __name__ == "__main__":
    main() 