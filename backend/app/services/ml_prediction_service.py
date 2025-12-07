"""
Machine Learning Prediction Service

Uses trained Random Forest model to predict student success probability.
Works as a hybrid with the existing rule-based prerequisite algorithm.
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class MLPrediction:
    """ML-based prediction result"""
    success_probability: float  # 0.0 - 1.0
    confidence: float  # Model confidence
    top_factors: List[Tuple[str, float]]  # Top contributing features
    risk_level: str  # 'low', 'medium', 'high', 'very_high'


class MLPredictionService:
    """Service for ML-based subject success prediction"""
    
    def __init__(self):
        self.model = None
        self.label_encoders = None
        self.feature_columns = None
        self.feature_importance = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained Random Forest model"""
        try:
            model_dir = Path(__file__).parent.parent.parent / 'models'
            
            # Load model
            model_path = model_dir / 'random_forest_model.pkl'
            if model_path.exists():
                self.model = joblib.load(model_path)
            
            # Load label encoders
            encoders_path = model_dir / 'label_encoders.pkl'
            if encoders_path.exists():
                self.label_encoders = joblib.load(encoders_path)
            
            # Load metadata
            metadata_path = model_dir / 'model_metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.feature_columns = metadata.get('feature_columns', [])
                    self.feature_importance = {
                        item['feature']: item['importance'] 
                        for item in metadata.get('feature_importance', [])
                    }
            
            if self.model is not None:
                # CRITICAL FIX: Disable parallel processing to prevent hanging
                # The model was trained with n_jobs=12 but during inference it hangs
                # Set n_jobs=1 to use single-threaded prediction (still fast enough)
                if hasattr(self.model, 'n_jobs'):
                    self.model.n_jobs = 1
                    print("✓ ML Model loaded successfully (single-threaded mode)")
                else:
                    print("✓ ML Model loaded successfully")
            else:
                print("⚠ ML Model not found - predictions will use rule-based only")
                
        except Exception as e:
            print(f"⚠ Error loading ML model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if ML model is loaded and available"""
        return self.model is not None
    
    def prepare_features(
        self,
        student_features: Dict,
        prereq_features: Dict,
        cohort_features: Dict,
        subject_code: str,
        programme_code: str = '',
        gender: str = '',
        cohort: int = 0,
        has_financial_aid: bool = False
    ) -> Optional[pd.DataFrame]:
        """Prepare features for ML prediction"""
        
        if not self.is_available():
            return None
        
        try:
            # Encode categorical features
            subject_code_encoded = 0
            if 'subject_code' in self.label_encoders:
                try:
                    subject_code_encoded = self.label_encoders['subject_code'].transform([subject_code])[0]
                except:
                    subject_code_encoded = -1  # Unknown subject
            
            programme_code_encoded = 0
            if 'programme_code' in self.label_encoders and programme_code:
                try:
                    programme_code_encoded = self.label_encoders['programme_code'].transform([programme_code])[0]
                except:
                    programme_code_encoded = -1  # Unknown programme
            
            gender_encoded = 0
            if 'gender' in self.label_encoders and gender:
                try:
                    gender_encoded = self.label_encoders['gender'].transform([gender])[0]
                except:
                    gender_encoded = -1  # Unknown gender
            
            # Create feature dictionary
            features = {
                # Student performance features
                'num_subjects_completed': student_features.get('num_subjects_completed', 0),
                'current_gpa': student_features.get('current_gpa', 0.0),
                'gpa_trend_last_3': student_features.get('gpa_trend_last_3', 0.0),
                'avg_coursework_percentage': student_features.get('avg_coursework_percentage', 0.0),
                'avg_overall_percentage': student_features.get('avg_overall_percentage', 0.0),
                'num_fails': student_features.get('num_fails', 0),
                'fail_rate': student_features.get('fail_rate', 0.0),
                
                # Prerequisite features
                'num_prerequisites': prereq_features.get('num_prerequisites', 0),
                'num_prerequisites_completed': prereq_features.get('num_prerequisites_completed', 0),
                'num_prerequisites_missing': prereq_features.get('num_prerequisites_missing', 0),
                'avg_prereq_grade_points': prereq_features.get('avg_prereq_grade_points', 0.0),
                'weighted_prereq_gpa': prereq_features.get('weighted_prereq_gpa', 0.0),
                'min_prereq_grade': prereq_features.get('min_prereq_grade', 0.0),
                'max_prereq_grade': prereq_features.get('max_prereq_grade', 0.0),
                
                # Subject cohort features
                'subject_pass_rate': cohort_features.get('subject_pass_rate', 0.5),
                'subject_avg_score': cohort_features.get('subject_avg_score', 50.0),
                'subject_avg_gpa': cohort_features.get('subject_avg_gpa', 2.0),
                'subject_total_students': cohort_features.get('subject_total_students', 0),
                
                # Encoded categorical features
                'programme_code_encoded': programme_code_encoded,
                'gender_encoded': gender_encoded,
                'subject_code_encoded': subject_code_encoded,
                
                # Additional features
                'cohort': cohort,
                'has_financial_aid': 1 if has_financial_aid else 0,
            }
            
            # Create DataFrame with correct column order
            X = pd.DataFrame([features])[self.feature_columns]
            return X
            
        except Exception as e:
            print(f"Error preparing features: {e}")
            return None
    
    def predict(
        self,
        student_features: Dict,
        prereq_features: Dict,
        cohort_features: Dict,
        subject_code: str,
        programme_code: str = '',
        gender: str = '',
        cohort: int = 0,
        has_financial_aid: bool = False
    ) -> Optional[MLPrediction]:
        """
        Make ML prediction for subject success
        
        Returns:
            MLPrediction object with probability and confidence, or None if model unavailable
        """
        
        if not self.is_available():
            return None
        
        try:
            # Prepare features
            X = self.prepare_features(
                student_features, prereq_features, cohort_features,
                subject_code, programme_code, gender, cohort, has_financial_aid
            )
            
            if X is None:
                return None
            
            # Get prediction probability
            proba = self.model.predict_proba(X)[0]
            success_probability = proba[1]  # Probability of passing
            
            # Calculate confidence (how certain the model is)
            # Higher confidence when probability is closer to 0 or 1
            confidence = abs(success_probability - 0.5) * 2
            
            # Determine risk level
            if success_probability >= 0.80:
                risk_level = 'low'
            elif success_probability >= 0.65:
                risk_level = 'medium'
            elif success_probability >= 0.50:
                risk_level = 'high'
            else:
                risk_level = 'very_high'
            
            # Identify top contributing factors
            top_factors = self._get_top_factors(X)
            
            return MLPrediction(
                success_probability=float(success_probability),
                confidence=float(confidence),
                top_factors=top_factors,
                risk_level=risk_level
            )
            
        except Exception as e:
            print(f"Error making ML prediction: {e}")
            return None
    
    def predict_batch(
        self,
        predictions_data: List[Dict]
    ) -> List[Optional[MLPrediction]]:
        """
        Make ML predictions for multiple subjects in a single batch (more efficient)
        
        Args:
            predictions_data: List of dicts containing:
                - student_features: Dict
                - prereq_features: Dict
                - cohort_features: Dict
                - subject_code: str
                - programme_code: str (optional)
                - gender: str (optional)
                - cohort: int (optional)
                - has_financial_aid: bool (optional)
        
        Returns:
            List of MLPrediction objects (None for failed predictions)
        """
        
        if not self.is_available():
            return [None] * len(predictions_data)
        
        try:
            # Prepare all features at once
            feature_dfs = []
            for data in predictions_data:
                X = self.prepare_features(
                    student_features=data['student_features'],
                    prereq_features=data['prereq_features'],
                    cohort_features=data['cohort_features'],
                    subject_code=data['subject_code'],
                    programme_code=data.get('programme_code', ''),
                    gender=data.get('gender', ''),
                    cohort=data.get('cohort', 0),
                    has_financial_aid=data.get('has_financial_aid', False)
                )
                feature_dfs.append(X)
            
            # Filter out None values
            valid_indices = [i for i, X in enumerate(feature_dfs) if X is not None]
            if not valid_indices:
                return [None] * len(predictions_data)
            
            valid_features = [feature_dfs[i] for i in valid_indices]
            
            # Batch inference - concatenate all features and predict once
            X_batch = pd.concat(valid_features, ignore_index=True)
            probas = self.model.predict_proba(X_batch)  # Single model call!
            
            # Process results
            results = [None] * len(predictions_data)
            for idx, i in enumerate(valid_indices):
                proba = probas[idx]
                success_probability = proba[1]
                confidence = abs(success_probability - 0.5) * 2
                
                # Determine risk level
                if success_probability >= 0.80:
                    risk_level = 'low'
                elif success_probability >= 0.65:
                    risk_level = 'medium'
                elif success_probability >= 0.50:
                    risk_level = 'high'
                else:
                    risk_level = 'very_high'
                
                # Get top factors
                top_factors = self._get_top_factors(valid_features[idx])
                
                results[i] = MLPrediction(
                    success_probability=float(success_probability),
                    confidence=float(confidence),
                    top_factors=top_factors,
                    risk_level=risk_level
                )
            
            return results
            
        except Exception as e:
            print(f"Error making batch ML predictions: {e}")
            return [None] * len(predictions_data)
    
    def _get_top_factors(self, X: pd.DataFrame, top_n: int = 5) -> List[Tuple[str, float]]:
        """Get top contributing factors for this prediction"""
        if self.feature_importance is None:
            return []
        
        try:
            # Get feature values
            feature_values = X.iloc[0].to_dict()
            
            # Calculate contribution (feature_value * feature_importance)
            contributions = []
            for feature, value in feature_values.items():
                importance = self.feature_importance.get(feature, 0.0)
                # Normalize contribution
                contrib = abs(value) * importance
                contributions.append((self._format_feature_name(feature), contrib))
            
            # Sort by contribution
            contributions.sort(key=lambda x: x[1], reverse=True)
            return contributions[:top_n]
            
        except Exception as e:
            print(f"Error calculating top factors: {e}")
            return []
    
    def _format_feature_name(self, feature: str) -> str:
        """Format feature name for display"""
        name_map = {
            'current_gpa': 'Current GPA',
            'subject_pass_rate': 'Subject Pass Rate',
            'subject_avg_gpa': 'Subject Difficulty',
            'fail_rate': 'Student Fail Rate',
            'cohort': 'Entry Cohort',
            'num_fails': 'Number of Fails',
            'avg_overall_percentage': 'Average Score',
            'avg_coursework_percentage': 'Coursework Performance',
            'num_subjects_completed': 'Subjects Completed',
            'gpa_trend_last_3': 'Recent GPA Trend',
            'weighted_prereq_gpa': 'Prerequisite Performance',
            'num_prerequisites_missing': 'Missing Prerequisites',
        }
        return name_map.get(feature, feature.replace('_', ' ').title())


# Singleton instance
_ml_service: Optional[MLPredictionService] = None

def get_ml_prediction_service() -> MLPredictionService:
    """Get or create ML prediction service singleton"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLPredictionService()
    return _ml_service
