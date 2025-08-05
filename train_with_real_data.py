#!/usr/bin/env python3
"""
NEET College Predictor - Train with Real Data
This script trains the prediction model using real historical NEET admission data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import json
import os
from datetime import datetime

class RealDataTrainer:
    def __init__(self):
        self.model_data = None
        self.real_data = None
        
    def load_real_data(self, csv_file='real_data_template.csv'):
        """Load real NEET historical data from CSV"""
        print(f"Loading real data from {csv_file}...")
        
        try:
            df = pd.read_csv(csv_file)
            print(f"✅ Loaded {len(df)} real records")
            print(f"Columns: {list(df.columns)}")
            return df
        except FileNotFoundError:
            print(f"❌ File {csv_file} not found")
            print("Please create the CSV file with real NEET data using the template")
            return None
    
    def preprocess_real_data(self, df):
        """Preprocess real data for training"""
        print("Preprocessing real data...")
        
        # Clean and validate data
        df_clean = df.copy()
        
        # Remove rows with missing values
        df_clean = df_clean.dropna()
        
        # Convert score ranges to average scores
        df_clean['avg_score'] = df_clean['Score_Range'].apply(self.extract_average_score)
        
        # Create training records
        training_data = []
        
        for _, row in df_clean.iterrows():
            # Create multiple records based on seat allocation
            seats = row['Allotted_Seats']
            if pd.isna(seats) or seats == 0:
                seats = 1
            
            for i in range(int(seats)):
                training_data.append({
                    'score': row['avg_score'],
                    'caste': row['Category'],
                    'state': row['State'],
                    'round': row['Counselling_Round'],
                    'college': row['College_Name'],
                    'year': row['Year'],
                    'opening_rank': row['Opening_Rank'],
                    'closing_rank': row['Closing_Rank']
                })
        
        training_df = pd.DataFrame(training_data)
        print(f"✅ Created {len(training_df)} training records")
        
        return training_df
    
    def extract_average_score(self, score_range):
        """Extract average score from score range string"""
        try:
            if pd.isna(score_range):
                return 500  # Default score
            
            # Handle different score range formats
            if '-' in str(score_range):
                parts = str(score_range).split('-')
                if len(parts) == 2:
                    high = float(parts[0])
                    low = float(parts[1])
                    return (high + low) / 2
                else:
                    return float(parts[0])
            else:
                return float(score_range)
        except:
            return 500  # Default score
    
    def train_model_with_real_data(self, df):
        """Train the model using real historical data"""
        print("Training model with real data...")
        
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
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest model
        print("Training Random Forest model...")
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate model
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        print(f"✅ Model training completed!")
        print(f"Training R² score: {train_score:.4f}")
        print(f"Testing R² score: {test_score:.4f}")
        
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
            'rounds': le_round.classes_.tolist(),
            'training_score': train_score,
            'testing_score': test_score,
            'data_source': 'Real NEET Historical Data',
            'training_date': datetime.now().isoformat()
        }
        
        with open('college_model_real.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        
        print("\n✅ Model saved to 'college_model_real.pkl'")
        
        # Save processed data
        df.to_csv('real_historical_data_processed.csv', index=False)
        print("✅ Processed data saved to 'real_historical_data_processed.csv'")
        
        return model_data
    
    def validate_real_data_quality(self, df):
        """Validate the quality of real data"""
        print("Validating real data quality...")
        
        validation_results = {
            'total_records': len(df),
            'missing_values': df.isnull().sum().to_dict(),
            'unique_colleges': len(df['College_Name'].unique()),
            'unique_states': len(df['State'].unique()),
            'unique_categories': len(df['Category'].unique()),
            'year_range': f"{df['Year'].min()} - {df['Year'].max()}",
            'score_range': f"{df['avg_score'].min():.0f} - {df['avg_score'].max():.0f}"
        }
        
        print("\nData Quality Report:")
        print(f"Total records: {validation_results['total_records']}")
        print(f"Unique colleges: {validation_results['unique_colleges']}")
        print(f"Unique states: {validation_results['unique_states']}")
        print(f"Year range: {validation_results['year_range']}")
        print(f"Score range: {validation_results['score_range']}")
        
        return validation_results
    
    def test_real_model_predictions(self, model_data):
        """Test the trained model with real-world scenarios"""
        print("\nTesting real model predictions...")
        
        test_cases = [
            {'score': 720, 'caste': 'General', 'state': 'Delhi', 'round': 'Round 1'},
            {'score': 680, 'caste': 'OBC', 'state': 'Maharashtra', 'round': 'Round 1'},
            {'score': 620, 'caste': 'SC', 'state': 'Karnataka', 'round': 'Round 2'},
            {'score': 580, 'caste': 'ST', 'state': 'Bihar', 'round': 'Mop Up'},
            {'score': 650, 'caste': 'EWS', 'state': 'Uttar Pradesh', 'round': 'Round 1'},
        ]
        
        print("\nPrediction Test Results:")
        print("-" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                # Encode inputs
                caste_encoded = model_data['le_caste'].transform([test_case['caste']])[0]
                state_encoded = model_data['le_state'].transform([test_case['state']])[0]
                round_encoded = model_data['le_round'].transform([test_case['round']])[0]
                
                # Make prediction
                features = np.array([[test_case['score'], caste_encoded, state_encoded, round_encoded]])
                prediction = model_data['model'].predict(features)[0]
                
                # Get predicted college
                predicted_college = model_data['le_college'].inverse_transform([int(prediction)])[0]
                
                print(f"Test {i}: Score {test_case['score']}, {test_case['caste']}, {test_case['state']}")
                print(f"  → Predicted: {predicted_college}")
                print()
                
            except Exception as e:
                print(f"Test {i}: Error - {e}")
                print()

def main():
    """Main function to train model with real data"""
    print("🎓 NEET College Predictor - Real Data Training")
    print("=" * 60)
    
    trainer = RealDataTrainer()
    
    # Load real data
    real_data = trainer.load_real_data()
    if real_data is None:
        print("\n📋 To use real data:")
        print("1. Download real NEET admission data from official sources")
        print("2. Format it according to the template in 'real_data_template.csv'")
        print("3. Save it as 'real_data_template.csv'")
        print("4. Run this script again")
        return
    
    # Validate data quality
    trainer.validate_real_data_quality(real_data)
    
    # Preprocess data
    processed_data = trainer.preprocess_real_data(real_data)
    
    # Train model
    model_data = trainer.train_model_with_real_data(processed_data)
    
    # Test predictions
    trainer.test_real_model_predictions(model_data)
    
    print("\n✅ Real data training completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update app.py to use 'college_model_real.pkl'")
    print("2. Test the website with real data predictions")
    print("3. Collect more historical data for better accuracy")

if __name__ == "__main__":
    main() 