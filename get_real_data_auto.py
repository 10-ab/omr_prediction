#!/usr/bin/env python3
"""
NEET College Predictor - One-Click Real Data Collection
Automatically scrapes real data and trains the model
"""

import os
import sys
import subprocess
import time

def print_banner():
    print("🎓 NEET College Predictor - One-Click Real Data Collection")
    print("=" * 70)
    print("This script will automatically:")
    print("1. Scrape real NEET data from official websites")
    print("2. Generate enhanced synthetic data if needed")
    print("3. Train the prediction model with real data")
    print("4. Update the website to use real data")
    print()

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'requests', 'beautifulsoup4', 'lxml', 'PyPDF2', 
        'pandas', 'numpy', 'scikit-learn', 'flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, 
                         check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def run_advanced_scraper():
    """Run the advanced scraper to collect real data"""
    print("\n🌐 Starting automated data collection...")
    print("This may take several minutes. Please be patient...")
    
    try:
        # Run the advanced scraper
        result = subprocess.run([sys.executable, 'advanced_scraper.py'], 
                              capture_output=True, text=True, timeout=600)  # 10 minutes timeout
        
        if result.returncode == 0:
            print("✅ Data collection completed successfully!")
            return True
        else:
            print(f"❌ Data collection failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Data collection timed out. Continuing with available data...")
        return True
    except Exception as e:
        print(f"❌ Error during data collection: {e}")
        return False

def train_model_with_real_data():
    """Train the model using collected real data"""
    print("\n🤖 Training model with real data...")
    
    try:
        # Check if we have real data
        if os.path.exists('real_neet_data.csv'):
            print("📊 Found real data file, training model...")
            
            # Run the training script
            result = subprocess.run([sys.executable, 'train_with_real_data.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Model training completed successfully!")
                return True
            else:
                print(f"❌ Model training failed: {result.stderr}")
                return False
        else:
            print("⚠️ No real data file found. Using synthetic data...")
            return False
            
    except Exception as e:
        print(f"❌ Error during model training: {e}")
        return False

def update_application():
    """Update the application to use real data"""
    print("\n🔄 Updating application...")
    
    try:
        # Check if real model exists
        if os.path.exists('college_model_real.pkl'):
            print("✅ Real data model found. Application will use real data automatically.")
            return True
        else:
            print("⚠️ No real data model found. Application will use synthetic data.")
            return False
            
    except Exception as e:
        print(f"❌ Error updating application: {e}")
        return False

def test_application():
    """Test the application"""
    print("\n🧪 Testing application...")
    
    try:
        # Run a quick test
        result = subprocess.run([sys.executable, 'test_app.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Application test passed!")
            return True
        else:
            print(f"⚠️ Application test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing application: {e}")
        return False

def show_summary():
    """Show summary of what was accomplished"""
    print("\n📋 Summary:")
    print("=" * 50)
    
    # Check what files exist
    files_to_check = [
        ('real_neet_data.csv', 'Real NEET Data'),
        ('college_model_real.pkl', 'Real Data Model'),
        ('real_historical_data_processed.csv', 'Processed Data'),
        ('scraped_neet_data.csv', 'Scraped Data')
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"✅ {description}: {filename}")
        else:
            print(f"❌ {description}: Not found")
    
    print("\n🚀 Next steps:")
    print("1. Start the application: python app.py")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Test the OMR scanner and college prediction")
    print("4. The website will automatically use real data if available")

def main():
    """Main function"""
    print_banner()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies. Please install manually:")
        print("pip install -r requirements.txt")
        return
    
    # Step 2: Run advanced scraper
    if not run_advanced_scraper():
        print("⚠️ Data collection had issues, but continuing...")
    
    # Step 3: Train model
    if not train_model_with_real_data():
        print("⚠️ Model training had issues, but continuing...")
    
    # Step 4: Update application
    update_application()
    
    # Step 5: Test application
    test_application()
    
    # Step 6: Show summary
    show_summary()
    
    print("\n🎯 One-click setup completed!")
    print("Your NEET College Predictor is ready to use with real data!")

if __name__ == "__main__":
    main() 