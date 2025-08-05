import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import random

def generate_historical_data(num_records=1000):
    """Generate realistic historical data for college predictions"""
    
    # Define realistic college data
    government_colleges = [
        'AIIMS Delhi', 'JIPMER Puducherry', 'MAMC Delhi', 'GMC Mumbai',
        'BHU Varanasi', 'AMU Aligarh', 'JNU Delhi', 'DU Delhi',
        'KGMU Lucknow', 'IMS BHU', 'LHMC Delhi', 'UCMS Delhi',
        'VMMC Delhi', 'Safdarjung Delhi', 'RML Delhi', 'Lady Hardinge Delhi'
    ]
    
    private_colleges = [
        'KMC Manipal', 'CMC Vellore', 'KIMS Bangalore', 'MS Ramaiah Bangalore',
        'SRM Chennai', 'VIT Vellore', 'Amrita Coimbatore', 'Manipal University',
        'JSS Mysore', 'KLE Belgaum', 'Bharati Vidyapeeth Pune', 'DY Patil Mumbai',
        'Padmashree Dr DY Patil Mumbai', 'Terna Mumbai', 'Seth GSMC Mumbai'
    ]
    
    all_colleges = government_colleges + private_colleges
    
    # Define states
    states = [
        'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Kerala', 'Delhi', 
        'Uttar Pradesh', 'Bihar', 'West Bengal', 'Gujarat', 'Rajasthan',
        'Andhra Pradesh', 'Telangana', 'Madhya Pradesh', 'Odisha', 'Punjab',
        'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Chhattisgarh', 'Assam'
    ]
    
    # Define categories
    categories = ['General', 'OBC', 'SC', 'ST', 'EWS']
    
    # Define counselling rounds
    rounds = ['Round 1', 'Round 2', 'Mop Up']
    
    # Generate realistic score distributions
    data = []
    
    for _ in range(num_records):
        # Generate score based on category
        category = random.choice(categories)
        
        if category == 'General':
            score = np.random.normal(650, 100)  # Higher scores for General
        elif category == 'OBC':
            score = np.random.normal(600, 100)
        elif category == 'SC':
            score = np.random.normal(550, 100)
        elif category == 'ST':
            score = np.random.normal(500, 100)
        else:  # EWS
            score = np.random.normal(620, 100)
        
        # Ensure score is within realistic bounds
        score = max(200, min(720, int(score)))
        
        # Select state
        state = random.choice(states)
        
        # Select counselling round
        round_type = random.choice(rounds)
        
        # Select college based on score and category
        if score >= 700:
            college = random.choice(government_colleges[:8])  # Top government colleges
        elif score >= 650:
            college = random.choice(government_colleges[8:12] + private_colleges[:5])
        elif score >= 600:
            college = random.choice(government_colleges[12:] + private_colleges[5:10])
        elif score >= 550:
            college = random.choice(private_colleges[10:])
        else:
            college = random.choice(private_colleges[-5:])  # Lower tier private colleges
        
        data.append({
            'score': score,
            'caste': category,
            'state': state,
            'round': round_type,
            'college': college
        })
    
    return pd.DataFrame(data)

def train_college_prediction_model():
    """Train the college prediction model with historical data"""
    
    print("Generating historical data...")
    df = generate_historical_data(2000)  # Generate 2000 records
    
    print(f"Generated {len(df)} historical records")
    print("\nData distribution:")
    print(f"Score range: {df['score'].min()} - {df['score'].max()}")
    print(f"Categories: {df['caste'].value_counts().to_dict()}")
    print(f"States: {len(df['state'].unique())}")
    print(f"Colleges: {len(df['college'].unique())}")
    
    # Encode categorical variables
    le_caste = LabelEncoder()
    le_state = LabelEncoder()
    le_round = LabelEncoder()
    le_college = LabelEncoder()
    
    df['caste_encoded'] = le_caste.fit_transform(df['caste'])
    df['state_encoded'] = le_state.fit_transform(df['state'])
    df['round_encoded'] = le_round.fit_transform(df['round'])
    df['college_encoded'] = le_college.fit_transform(df['college'])
    
    # Prepare features and target
    X = df[['score', 'caste_encoded', 'state_encoded', 'round_encoded']]
    y = df['college_encoded']
    
    # Train Random Forest model
    print("\nTraining Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    model.fit(X, y)
    
    # Calculate model performance
    train_score = model.score(X, y)
    print(f"Model R² score: {train_score:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': ['Score', 'Category', 'State', 'Round'],
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature importance:")
    for _, row in feature_importance.iterrows():
        print(f"{row['feature']}: {row['importance']:.4f}")
    
    # Save model and encoders
    model_data = {
        'model': model,
        'le_caste': le_caste,
        'le_state': le_state,
        'le_round': le_round,
        'le_college': le_college,
        'colleges': le_college.classes_.tolist(),
        'states': le_state.classes_.tolist(),
        'categories': le_caste.classes_.tolist(),
        'rounds': le_round.classes_.tolist()
    }
    
    with open('college_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("\nModel saved to 'college_model.pkl'")
    
    # Save historical data for reference
    df.to_csv('historical_data.csv', index=False)
    print("Historical data saved to 'historical_data.csv'")
    
    return model_data

def test_model_predictions():
    """Test the trained model with sample inputs"""
    
    # Load the trained model
    with open('college_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
    
    # Test cases
    test_cases = [
        {'score': 720, 'caste': 'General', 'state': 'Delhi', 'round': 'Round 1'},
        {'score': 650, 'caste': 'OBC', 'state': 'Maharashtra', 'round': 'Round 2'},
        {'score': 580, 'caste': 'SC', 'state': 'Karnataka', 'round': 'Mop Up'},
        {'score': 450, 'caste': 'General', 'state': 'Bihar', 'round': 'Round 1'},
    ]
    
    print("\nTesting model predictions:")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        # Encode inputs
        caste_encoded = model_data['le_caste'].transform([test_case['caste']])[0]
        state_encoded = model_data['le_state'].transform([test_case['state']])[0]
        round_encoded = model_data['le_round'].transform([test_case['round']])[0]
        
        # Make prediction
        features = np.array([[test_case['score'], caste_encoded, state_encoded, round_encoded]])
        prediction = model_data['model'].predict(features)[0]
        
        # Get predicted college
        predicted_college = model_data['le_college'].inverse_transform([int(prediction)])[0]
        
        print(f"Test {i}:")
        print(f"  Score: {test_case['score']}, Category: {test_case['caste']}")
        print(f"  State: {test_case['state']}, Round: {test_case['round']}")
        print(f"  Predicted College: {predicted_college}")
        print()

if __name__ == "__main__":
    print("NEET College Predictor - Model Training")
    print("=" * 50)
    
    # Train the model
    model_data = train_college_prediction_model()
    
    # Test predictions
    test_model_predictions()
    
    print("Training completed successfully!") 