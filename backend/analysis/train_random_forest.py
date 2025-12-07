"""
Train Random Forest Model for Subject Success Prediction

This script trains a Random Forest classifier to predict whether a student
will pass a subject based on their historical performance and other features.

The model is designed to work as a hybrid with the existing rule-based
prerequisite algorithm.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score,
    accuracy_score
)
import json


def load_training_data(data_path):
    """Load the prepared ML training data"""
    print("Loading ML training data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df):,} records")
    print(f"  - Unique students: {df['student_id'].nunique():,}")
    print(f"  - Unique subjects: {df['subject_code'].nunique():,}")
    return df


def prepare_features(df):
    """Prepare features for training"""
    print("\nPreparing features...")
    
    # Encode categorical features
    label_encoders = {}
    
    # Programme code
    if 'programme_code' in df.columns:
        le_prog = LabelEncoder()
        df['programme_code_encoded'] = le_prog.fit_transform(df['programme_code'].fillna('UNKNOWN'))
        label_encoders['programme_code'] = le_prog
    
    # Gender
    if 'gender' in df.columns:
        le_gender = LabelEncoder()
        df['gender_encoded'] = le_gender.fit_transform(df['gender'].fillna('UNKNOWN'))
        label_encoders['gender'] = le_gender
    
    # Subject code (important for learning subject-specific patterns)
    le_subject = LabelEncoder()
    df['subject_code_encoded'] = le_subject.fit_transform(df['subject_code'])
    label_encoders['subject_code'] = le_subject
    
    # Select features for training
    feature_columns = [
        # Student performance features
        'num_subjects_completed',
        'current_gpa',
        'gpa_trend_last_3',
        'avg_coursework_percentage',
        'avg_overall_percentage',
        'num_fails',
        'fail_rate',
        
        # Prerequisite features (from existing algorithm)
        'num_prerequisites',
        'num_prerequisites_completed',
        'num_prerequisites_missing',
        'avg_prereq_grade_points',
        'weighted_prereq_gpa',
        'min_prereq_grade',
        'max_prereq_grade',
        
        # Subject cohort features
        'subject_pass_rate',
        'subject_avg_score',
        'subject_avg_gpa',
        'subject_total_students',
        
        # Encoded categorical features
        'programme_code_encoded',
        'gender_encoded',
        'subject_code_encoded',
        
        # Additional features
        'cohort',
        'has_financial_aid',
    ]
    
    # Handle missing values
    X = df[feature_columns].fillna(0)
    y = df['passed']
    
    print(f"✓ Features prepared: {len(feature_columns)} features")
    print(f"  - Class distribution: Pass={y.sum():,} ({y.mean()*100:.1f}%), Fail={len(y)-y.sum():,} ({(1-y.mean())*100:.1f}%)")
    
    return X, y, feature_columns, label_encoders


def train_model(X, y):
    """Train Random Forest model with cross-validation"""
    print("\nSplitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✓ Training set: {len(X_train):,} records")
    print(f"✓ Test set: {len(X_test):,} records")
    
    print("\nTraining Random Forest model...")
    print("  Parameters: 100 trees, max_depth=20, class_weight=balanced")
    
    # Train Random Forest with balanced class weights
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=4,
        class_weight='balanced',  # Handle class imbalance
        random_state=42,
        n_jobs=-1,  # Use all CPU cores
        verbose=1
    )
    
    rf_model.fit(X_train, y_train)
    print("✓ Model trained!")
    
    return rf_model, X_train, X_test, y_train, y_test


def evaluate_model(model, X_train, X_test, y_train, y_test, feature_columns):
    """Evaluate model performance"""
    print("\n" + "="*70)
    print("MODEL EVALUATION")
    print("="*70)
    
    # Training accuracy
    train_pred = model.predict(X_train)
    train_acc = accuracy_score(y_train, train_pred)
    print(f"\n📊 Training Accuracy: {train_acc*100:.2f}%")
    
    # Test accuracy
    test_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, test_pred)
    print(f"📊 Test Accuracy: {test_acc*100:.2f}%")
    
    # ROC-AUC Score
    test_proba = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, test_proba)
    print(f"📊 ROC-AUC Score: {roc_auc:.4f}")
    
    # Classification report
    print("\n📋 Classification Report (Test Set):")
    print(classification_report(y_test, test_pred, target_names=['Fail', 'Pass']))
    
    # Confusion matrix
    print("📋 Confusion Matrix:")
    cm = confusion_matrix(y_test, test_pred)
    print(f"                Predicted")
    print(f"                Fail    Pass")
    print(f"Actual Fail    {cm[0][0]:5d}   {cm[0][1]:5d}")
    print(f"Actual Pass    {cm[1][0]:5d}   {cm[1][1]:5d}")
    
    # Feature importance
    print("\n🎯 Top 15 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(15).iterrows():
        print(f"  {row['feature']:40s} {row['importance']:.4f}")
    
    return feature_importance


def save_model(model, label_encoders, feature_columns, feature_importance, output_dir):
    """Save trained model and metadata"""
    print("\n💾 Saving model and metadata...")
    
    # Save model
    model_path = output_dir / 'random_forest_model.pkl'
    joblib.dump(model, model_path)
    print(f"✓ Model saved: {model_path}")
    
    # Save label encoders
    encoders_path = output_dir / 'label_encoders.pkl'
    joblib.dump(label_encoders, encoders_path)
    print(f"✓ Label encoders saved: {encoders_path}")
    
    # Save feature metadata
    metadata = {
        'feature_columns': feature_columns,
        'model_type': 'RandomForestClassifier',
        'n_estimators': model.n_estimators,
        'max_depth': model.max_depth,
        'feature_importance': feature_importance.to_dict('records')
    }
    
    metadata_path = output_dir / 'model_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {metadata_path}")


def main():
    """Main execution"""
    # Paths
    data_dir = Path(__file__).parent.parent / 'data'
    model_dir = Path(__file__).parent.parent / 'models'
    model_dir.mkdir(exist_ok=True)
    
    training_data_path = data_dir / 'ml_training_data.csv'
    
    if not training_data_path.exists():
        print(f"ERROR: Training data not found at {training_data_path}")
        print("Please run prepare_ml_data_from_cassandra.py first!")
        return
    
    # Load data
    df = load_training_data(training_data_path)
    
    # Prepare features
    X, y, feature_columns, label_encoders = prepare_features(df)
    
    # Train model
    model, X_train, X_test, y_train, y_test = train_model(X, y)
    
    # Evaluate model
    feature_importance = evaluate_model(model, X_train, X_test, y_train, y_test, feature_columns)
    
    # Save model
    save_model(model, label_encoders, feature_columns, feature_importance, model_dir)
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review model performance metrics above")
    print("2. Integrate ML predictions with existing rule-based algorithm")
    print("3. Create hybrid prediction service")
    print("="*70)


if __name__ == "__main__":
    main()
