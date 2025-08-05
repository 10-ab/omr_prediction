from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import cv2
import numpy as np
from PIL import Image
import json
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import base64
import io
from datetime import datetime
from omr_processor import omr_processor

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load college data
def load_college_data():
    try:
        with open('static/data/colleges.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

college_data = load_college_data()

# Load or create the college prediction model
def load_or_create_model(model_file='college_model.pkl'):
    """Load existing model or create new one"""
    try:
        with open(model_file, 'rb') as f:
            model_data = pickle.load(f)
            print(f"✅ Loaded model from {model_file}")
            if 'data_source' in model_data:
                print(f"📊 Data source: {model_data['data_source']}")
            return model_data
    except FileNotFoundError:
        print(f"Model {model_file} not found, creating new one...")
        return create_initial_model()

def create_initial_model():
    """Create initial model with sample data"""
    # Sample historical data (in real scenario, this would be much larger)
    data = {
        'score': [720, 680, 650, 600, 550, 500, 450, 400, 350, 300],
        'caste': ['General', 'OBC', 'SC', 'ST', 'General', 'OBC', 'SC', 'ST', 'General', 'OBC'],
        'state': ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Kerala', 'Delhi', 'UP', 'Bihar', 'West Bengal', 'Gujarat', 'Rajasthan'],
        'round': ['Round 1', 'Round 2', 'Mop Up', 'Round 1', 'Round 2', 'Mop Up', 'Round 1', 'Round 2', 'Mop Up', 'Round 1'],
        'college': ['AIIMS Delhi', 'JIPMER Puducherry', 'MAMC Delhi', 'GMC Mumbai', 'KMC Manipal', 'CMC Vellore', 'BHU Varanasi', 'AMU Aligarh', 'JNU Delhi', 'DU Delhi']
    }
    
    df = pd.DataFrame(data)
    
    # Encode categorical variables
    le_caste = LabelEncoder()
    le_state = LabelEncoder()
    le_round = LabelEncoder()
    le_college = LabelEncoder()
    
    df['caste_encoded'] = le_caste.fit_transform(df['caste'])
    df['state_encoded'] = le_state.fit_transform(df['state'])
    df['round_encoded'] = le_round.fit_transform(df['round'])
    df['college_encoded'] = le_college.fit_transform(df['college'])
    
    # Train model
    X = df[['score', 'caste_encoded', 'state_encoded', 'round_encoded']]
    y = df['college_encoded']
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save model and encoders
    model_data = {
        'model': model,
        'le_caste': le_caste,
        'le_state': le_state,
        'le_round': le_round,
        'le_college': le_college
    }
    
    with open('college_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    return model_data

# Load model at startup (try real data first, fallback to synthetic)
def load_best_available_model():
    """Load the best available model (real data > enhanced synthetic > basic synthetic)"""
    model_files = [
        ('college_model_real.pkl', 'Real Historical Data'),
        ('college_model_enhanced.pkl', 'Enhanced Synthetic Data'),
        ('college_model.pkl', 'Basic Synthetic Data')
    ]
    
    for model_file, data_type in model_files:
        try:
            model_data = load_or_create_model(model_file)
            print(f"🎯 Using {data_type} model: {model_file}")
            return model_data
        except Exception as e:
            print(f"⚠️ Could not load {model_file}: {e}")
            continue
    
    # If all fail, create a basic model
    print("📊 Creating basic synthetic data model")
    return create_initial_model()

model_data = load_best_available_model()

def process_omr_image(image_path):
    """Process OMR sheet and return answers using advanced OMR processor"""
    try:
        # Use the advanced OMR processor
        answers, error = omr_processor.process_omr_sheet(image_path)
        
        if error:
            return None, error
        
        # Validate answers
        is_valid, validation_msg = omr_processor.validate_answers(answers)
        if not is_valid:
            return None, validation_msg
        
        return answers, None
    except Exception as e:
        return None, str(e)

def calculate_score(answers, correct_answers):
    """Calculate score based on answers"""
    score = 0
    correct_count = 0
    incorrect_count = 0
    unattempted_count = 0
    
    for i, (student_answer, correct_answer) in enumerate(zip(answers, correct_answers)):
        if student_answer == '':
            unattempted_count += 1
        elif student_answer == correct_answer:
            score += 3
            correct_count += 1
        else:
            score -= 1
            incorrect_count += 1
    
    return {
        'total_score': score,
        'correct_answers': correct_count,
        'incorrect_answers': incorrect_count,
        'unattempted_questions': unattempted_count,
        'total_questions': len(answers)
    }

def predict_colleges(score, caste, state, round_type):
    """Predict colleges based on score and other parameters"""
    try:
        # Encode inputs
        caste_encoded = model_data['le_caste'].transform([caste])[0]
        state_encoded = model_data['le_state'].transform([state])[0]
        round_encoded = model_data['le_round'].transform([round_type])[0]
        
        # Make prediction
        features = np.array([[score, caste_encoded, state_encoded, round_encoded]])
        prediction = model_data['model'].predict(features)[0]
        
        # Get predicted college
        predicted_college = model_data['le_college'].inverse_transform([int(prediction)])[0]
        
        # Generate additional college suggestions based on score
        colleges = []
        
        # Government Medical Colleges
        govt_colleges = [
            'AIIMS Delhi', 'JIPMER Puducherry', 'MAMC Delhi', 'GMC Mumbai',
            'BHU Varanasi', 'AMU Aligarh', 'JNU Delhi', 'DU Delhi',
            'KGMU Lucknow', 'IMS BHU', 'MAMC Delhi', 'LHMC Delhi'
        ]
        
        # Private Medical Colleges
        private_colleges = [
            'KMC Manipal', 'CMC Vellore', 'KIMS Bangalore', 'MS Ramaiah Bangalore',
            'SRM Chennai', 'VIT Vellore', 'Amrita Coimbatore', 'Manipal University'
        ]
        
        # Score-based recommendations
        if score >= 700:
            colleges.extend(govt_colleges[:6])
        elif score >= 600:
            colleges.extend(govt_colleges[6:10])
            colleges.extend(private_colleges[:4])
        elif score >= 500:
            colleges.extend(govt_colleges[10:])
            colleges.extend(private_colleges[4:])
        else:
            colleges.extend(private_colleges)
        
        return {
            'predicted_college': predicted_college,
            'recommended_colleges': colleges[:10],  # Top 10 recommendations
            'confidence': min(0.95, 0.5 + (score / 1000))  # Higher score = higher confidence
        }
    except Exception as e:
        return {
            'predicted_college': 'Unable to predict',
            'recommended_colleges': [],
            'confidence': 0.0,
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_omr', methods=['POST'])
def upload_omr():
    try:
        if 'omr_image' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['omr_image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = f"omr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process OMR
        answers, error = process_omr_image(filepath)
        if error:
            return jsonify({'error': error}), 400
        
        # For demo, use sample correct answers
        correct_answers = ['A', 'B', 'C', 'D'] * 50  # 200 questions
        
        # Calculate score
        score_result = calculate_score(answers, correct_answers)
        
        return jsonify({
            'success': True,
            'answers': answers,
            'score_result': score_result,
            'filename': filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict_colleges', methods=['POST'])
def predict_colleges_route():
    try:
        data = request.get_json()
        score = data.get('score', 0)
        caste = data.get('caste', 'General')
        state = data.get('state', 'Maharashtra')
        round_type = data.get('round', 'Round 1')
        
        prediction = predict_colleges(score, caste, state, round_type)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_states')
def get_states():
    if college_data:
        return jsonify({'states': college_data['states']})
    else:
        states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
            'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
            'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi'
        ]
        return jsonify({'states': states})

@app.route('/get_colleges')
def get_colleges():
    if college_data:
        return jsonify(college_data)
    else:
        return jsonify({'error': 'College data not available'})

@app.route('/get_data_status')
def get_data_status():
    """Get status of available data and model information"""
    try:
        status = {
            'data_files': [],
            'model_files': [],
            'data_quality': 'Unknown',
            'model_info': {}
        }
        
        # Check for data files
        data_files = [
            'real_neet_data.csv',
            'scraped_neet_data.csv',
            'real_data_template.csv'
        ]
        
        for file in data_files:
            if os.path.exists(file):
                status['data_files'].append(file)
        
        # Check for model files
        model_files = [
            'college_model_real.pkl',
            'college_model_enhanced.pkl',
            'college_model.pkl'
        ]
        
        for file in model_files:
            if os.path.exists(file):
                status['model_files'].append(file)
        
        # Determine data quality
        if len(status['data_files']) > 0:
            status['data_quality'] = 'Real Data Available'
        elif len(status['model_files']) > 0:
            status['data_quality'] = 'Synthetic Data'
        else:
            status['data_quality'] = 'No Data'
        
        # Get model information
        if 'model_data' in globals():
            status['model_info'] = {
                'colleges_count': len(model_data.get('colleges', [])),
                'states_count': len(model_data.get('states', [])),
                'categories_count': len(model_data.get('categories', [])),
                'rounds_count': len(model_data.get('rounds', [])),
                'data_source': model_data.get('data_source', 'Unknown'),
                'training_date': model_data.get('training_date', 'Unknown')
            }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 