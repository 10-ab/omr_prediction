#!/usr/bin/env python3
"""
Test script for NEET College Predictor
"""

import requests
import json
import os
import time

def test_server_connection():
    """Test if the server is running"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the app is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def test_states_endpoint():
    """Test the states endpoint"""
    try:
        response = requests.get('http://localhost:5000/get_states', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'states' in data and len(data['states']) > 0:
                print(f"✅ States endpoint working - {len(data['states'])} states available")
                return True
            else:
                print("❌ States endpoint returned empty data")
                return False
        else:
            print(f"❌ States endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing states endpoint: {e}")
        return False

def test_college_prediction():
    """Test college prediction functionality"""
    try:
        test_data = {
            'score': 650,
            'caste': 'General',
            'state': 'Maharashtra',
            'round': 'Round 1'
        }
        
        response = requests.post(
            'http://localhost:5000/predict_colleges',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'prediction' in data:
                prediction = data['prediction']
                print(f"✅ College prediction working")
                print(f"   Predicted college: {prediction.get('predicted_college', 'N/A')}")
                print(f"   Confidence: {prediction.get('confidence', 0):.2f}")
                print(f"   Recommended colleges: {len(prediction.get('recommended_colleges', []))}")
                return True
            else:
                print("❌ College prediction returned invalid data")
                return False
        else:
            print(f"❌ College prediction returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing college prediction: {e}")
        return False

def test_omr_upload():
    """Test OMR upload functionality (simulated)"""
    try:
        # Create a simple test image
        from PIL import Image, ImageDraw
        
        # Create a white image with some circles
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some circles to simulate OMR bubbles
        for i in range(10):
            x = 100 + (i * 60)
            y = 100
            draw.ellipse([x, y, x+20, y+20], outline='black', width=2)
        
        # Save test image
        test_image_path = 'test_omr.jpg'
        img.save(test_image_path)
        
        # Test upload
        with open(test_image_path, 'rb') as f:
            files = {'omr_image': f}
            response = requests.post('http://localhost:5000/upload_omr', files=files, timeout=10)
        
        # Clean up test image
        os.remove(test_image_path)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'score_result' in data:
                score_result = data['score_result']
                print(f"✅ OMR upload working")
                print(f"   Total score: {score_result.get('total_score', 0)}")
                print(f"   Correct answers: {score_result.get('correct_answers', 0)}")
                print(f"   Incorrect answers: {score_result.get('incorrect_answers', 0)}")
                return True
            else:
                print("❌ OMR upload returned invalid data")
                return False
        else:
            print(f"❌ OMR upload returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing OMR upload: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing NEET College Predictor")
    print("=" * 50)
    
    tests = [
        ("Server Connection", test_server_connection),
        ("States Endpoint", test_states_endpoint),
        ("College Prediction", test_college_prediction),
        ("OMR Upload", test_omr_upload)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the application setup.")
    
    return passed == total

if __name__ == "__main__":
    main() 