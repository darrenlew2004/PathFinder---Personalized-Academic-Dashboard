"""
Test Hybrid Prediction System

Tests the integrated Random Forest + Rule-based hybrid prediction system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.subject_prediction_service import get_prediction_service


def test_hybrid_predictions():
    """Test hybrid predictions for sample students"""
    
    print("="*70)
    print("TESTING HYBRID PREDICTION SYSTEM")
    print("="*70)
    
    # Get prediction service
    service = get_prediction_service()
    
    # Test student IDs (from the dataset)
    test_students = [
        (9897587, "CSC3206"),  # Student taking AI
        (2733926, "NET3106"),  # Student taking Network Security
        (2721492, "CSC2103"),  # Student taking Data Structures
    ]
    
    for student_id, subject_code in test_students:
        print(f"\n{'='*70}")
        print(f"PREDICTION FOR STUDENT {student_id} → {subject_code}")
        print(f"{'='*70}")
        
        try:
            # Get prediction
            prediction = service.predict_subject_success(student_id, subject_code)
            
            if prediction:
                print(f"\n📊 Subject: {prediction.subject_name} ({prediction.subject_code})")
                print(f"🎯 Prediction Method: {prediction.prediction_method.upper()}")
                print(f"\n--- RULE-BASED ANALYSIS ---")
                print(f"Risk Level: {prediction.risk_level.upper()}")
                print(f"Success Probability: {prediction.predicted_success_probability*100:.1f}%")
                print(f"Weighted Prereq GPA: {prediction.weighted_prereq_gpa:.2f}")
                print(f"Prerequisites: {len(prediction.prereq_performance)} completed, {len(prediction.missing_prereqs)} missing")
                
                if prediction.ml_probability is not None:
                    print(f"\n--- MACHINE LEARNING ANALYSIS ---")
                    print(f"ML Success Probability: {prediction.ml_probability*100:.1f}%")
                    print(f"ML Confidence: {prediction.ml_confidence*100:.0f}%")
                    if prediction.ml_top_factors:
                        print(f"Top Contributing Factors:")
                        for i, (factor, score) in enumerate(prediction.ml_top_factors[:5], 1):
                            print(f"  {i}. {factor}")
                else:
                    print(f"\n⚠ ML prediction not available (using rule-based only)")
                
                print(f"\n💡 Recommendation:")
                print(prediction.recommendation)
                
                print(f"\n📈 Cohort Statistics:")
                if prediction.cohort_pass_rate:
                    print(f"  Pass Rate: {prediction.cohort_pass_rate*100:.1f}%")
                if prediction.cohort_avg_score:
                    print(f"  Average Score: {prediction.cohort_avg_score:.1f}%")
            else:
                print(f"❌ No prediction available for this student/subject")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print(f"{'='*70}\n")


def test_ml_service_directly():
    """Test ML service directly"""
    print("\n" + "="*70)
    print("TESTING ML SERVICE DIRECTLY")
    print("="*70)
    
    try:
        from app.services.ml_prediction_service import get_ml_prediction_service
        
        ml_service = get_ml_prediction_service()
        
        if ml_service.is_available():
            print("✅ ML Model is loaded and available")
            print(f"   Features: {len(ml_service.feature_columns)}")
            print(f"   Top features: {', '.join(list(ml_service.feature_importance.keys())[:5])}")
        else:
            print("⚠ ML Model is NOT available")
            
    except Exception as e:
        print(f"❌ Error loading ML service: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Test ML service first
    test_ml_service_directly()
    
    # Then test hybrid predictions
    test_hybrid_predictions()
