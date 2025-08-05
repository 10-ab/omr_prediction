#!/usr/bin/env python3
"""
NEET College Predictor - Get Real Data
Simple script to help you get started with real data collection
"""

import os
import webbrowser
import time

def print_banner():
    print("🎓 NEET College Predictor - Real Data Collection")
    print("=" * 60)
    print("This script will help you collect real NEET historical data")
    print("to improve prediction accuracy.")
    print()

def show_data_sources():
    print("📊 Main Data Sources:")
    print("1. Medical Counselling Committee (MCC)")
    print("2. National Testing Agency (NTA)")
    print("3. State Counselling Websites")
    print("4. College Websites")
    print("5. Public Datasets")
    print()

def open_data_sources():
    """Open data source websites in browser"""
    sources = {
        "MCC Website": "https://mcc.nic.in/",
        "NTA NEET": "https://neet.nta.nic.in/",
        "Data.gov.in": "https://data.gov.in/",
        "Kaggle Datasets": "https://www.kaggle.com/datasets"
    }
    
    print("🌐 Opening data source websites...")
    for name, url in sources.items():
        print(f"Opening {name}...")
        webbrowser.open(url)
        time.sleep(1)
    
    print("✅ All websites opened in your browser")
    print()

def show_template_info():
    print("📋 Data Template Information:")
    print("- Template file: real_data_template.csv")
    print("- Required columns: Year, College_Name, State, Category, etc.")
    print("- Sample data included for reference")
    print("- Use Excel or Google Sheets for easy editing")
    print()

def show_next_steps():
    print("🚀 Next Steps:")
    print("1. Visit the opened websites")
    print("2. Download admission data (PDF/Excel files)")
    print("3. Extract required information")
    print("4. Enter data in real_data_template.csv")
    print("5. Run: python train_with_real_data.py")
    print("6. Test the website with real data")
    print()

def check_existing_files():
    print("📁 Checking existing files...")
    
    files_to_check = [
        'real_data_template.csv',
        'college_model_real.pkl',
        'real_historical_data_processed.csv'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} not found")
    
    print()

def main():
    print_banner()
    
    # Check existing files
    check_existing_files()
    
    # Show information
    show_data_sources()
    show_template_info()
    
    # Ask user if they want to open websites
    response = input("Do you want to open data source websites? (y/n): ").lower()
    if response in ['y', 'yes']:
        open_data_sources()
    
    show_next_steps()
    
    print("💡 Tips for data collection:")
    print("- Start with 1-2 states to test the process")
    print("- Focus on recent years (2020-2024) first")
    print("- Ensure data consistency across sources")
    print("- Validate data accuracy before training")
    print()
    
    print("📞 Need help? Check REAL_DATA_GUIDE.md for detailed instructions")
    print("🎯 Good luck with your data collection!")

if __name__ == "__main__":
    main() 