"""
Comprehensive Test Suite for PathFinder Academic Dashboard

This combines all test files:
- test_hybrid_predictions.py - Tests ML + rule-based hybrid predictions
- test_batch_performance.py - Tests batch vs individual prediction performance
- test_api_performance.py - Tests API endpoint performance
- test_academic_planner.py - Tests academic planning with ML predictions
"""

import sys
import time
import requests
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.subject_prediction_service import get_prediction_service
from app.services.csv_data_service import get_csv_service
from app.catalog.bcs_programs import load_bcs_variants


# ============================================================================
# TEST 1: HYBRID PREDICTION SYSTEM
# ============================================================================

def test_hybrid_predictions():
    """Test hybrid predictions for sample students"""
    
    print("\n" + "="*70)
    print("TEST 1: HYBRID PREDICTION SYSTEM")
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
    print("✅ TEST 1 COMPLETE")
    print(f"{'='*70}\n")


def test_ml_service_directly():
    """Test ML service directly"""
    print("\n" + "="*70)
    print("TESTING ML SERVICE AVAILABILITY")
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


# ============================================================================
# TEST 2: BATCH PERFORMANCE
# ============================================================================

def test_batch_performance():
    """Compare batch vs individual prediction performance"""
    
    print("\n" + "="*70)
    print("TEST 2: BATCH PERFORMANCE")
    print("="*70)
    
    service = get_prediction_service()
    
    if service.df is None:
        print("❌ Data not loaded!")
        return
    
    # Test parameters
    test_student_id = 9897587
    test_subjects = ['CSC3206', 'NET2201', 'CSC3044', 'SEC3024', 'CSC3034']
    
    print(f"\nStudent ID: {test_student_id}")
    print(f"Subjects: {', '.join(test_subjects)}")
    print()
    
    # Clear caches for fair comparison
    if hasattr(service, '_student_cache'):
        service._student_cache.clear()
    if hasattr(service, '_student_perf_cache'):
        service._student_perf_cache.clear()
    
    # Test 1: Batch inference (optimized with caching)
    print("🚀 Batch Inference (with caching)")
    start_time = time.time()
    
    report = service.predict_multiple_subjects(test_student_id, test_subjects)
    
    batch_time = time.time() - start_time
    print(f"   Time: {batch_time:.4f} seconds")
    print(f"   Predictions: {len(report.predictions)}")
    print(f"   Method: {report.predictions[0].prediction_method if report.predictions else 'N/A'}")
    print()
    
    # Display results
    print("📊 Results:")
    for pred in report.predictions:
        print(f"   {pred.subject_code}: {pred.predicted_success_probability*100:.1f}% "
              f"(Risk: {pred.risk_level})")
    print()
    
    # Clear caches again
    service._student_cache.clear()
    service._student_perf_cache.clear()
    
    # Test 2: Individual predictions (old way)
    print("🐌 Individual Predictions (no batch)")
    start_time = time.time()
    
    predictions = []
    for subject_code in test_subjects:
        pred = service.predict_subject_success(test_student_id, subject_code)
        predictions.append(pred)
    
    individual_time = time.time() - start_time
    print(f"   Time: {individual_time:.4f} seconds")
    print(f"   Predictions: {len(predictions)}")
    print()
    
    # Performance comparison
    print("📈 Performance Comparison")
    print("-" * 70)
    print(f"Batch inference:       {batch_time:.4f}s")
    print(f"Individual predictions: {individual_time:.4f}s")
    
    if batch_time < individual_time:
        speedup = individual_time / batch_time
        improvement = ((individual_time - batch_time) / individual_time) * 100
        print(f"✅ Speedup: {speedup:.2f}x faster ({improvement:.1f}% improvement)")
    else:
        print("⚠️  Batch inference was slower (unexpected)")
    
    print()
    
    # Test 3: Cache effectiveness
    print("🧠 Cache Effectiveness Test")
    print("-" * 70)
    
    # First call (cache miss)
    start_time = time.time()
    report1 = service.predict_multiple_subjects(test_student_id, test_subjects)
    first_call_time = time.time() - start_time
    
    # Second call (cache hit)
    start_time = time.time()
    report2 = service.predict_multiple_subjects(test_student_id, test_subjects)
    second_call_time = time.time() - start_time
    
    print(f"First call (cache miss):  {first_call_time:.4f}s")
    print(f"Second call (cache hit):  {second_call_time:.4f}s")
    
    if second_call_time < first_call_time:
        cache_speedup = first_call_time / second_call_time
        cache_improvement = ((first_call_time - second_call_time) / first_call_time) * 100
        print(f"✅ Cache speedup: {cache_speedup:.2f}x faster ({cache_improvement:.1f}% improvement)")
    
    print()
    
    # Test 4: ML Batch vs Individual
    if service.ml_service and service.ml_service.is_available():
        print("🤖 ML Model: Batch vs Individual Inference")
        print("-" * 70)
        
        # Prepare test data
        student_subjects = service._get_student_subjects(test_student_id)
        student_features = service._get_cached_student_performance(test_student_id, student_subjects)
        
        from app.services.subject_prediction_service import SUBJECT_PREREQUISITES
        import numpy as np
        
        batch_data = []
        for code in test_subjects:
            prereqs = SUBJECT_PREREQUISITES.get(code, [])
            
            prereq_performance = []
            missing_prereqs = []
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for prereq_code, weight in prereqs:
                if prereq_code in student_subjects:
                    subj = student_subjects[prereq_code]
                    gp = subj['grade_points']
                    if gp is not None:
                        prereq_performance.append((prereq_code, gp, weight))
                        total_weighted_score += gp * weight
                        total_weight += weight
                else:
                    missing_prereqs.append(prereq_code)
            
            weighted_prereq_gpa = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            prereq_features = {
                'num_prerequisites': len(prereqs),
                'num_prerequisites_completed': len(prereq_performance),
                'num_prerequisites_missing': len(missing_prereqs),
                'avg_prereq_grade_points': np.mean([p[1] for p in prereq_performance]) if prereq_performance else 0.0,
                'weighted_prereq_gpa': weighted_prereq_gpa,
                'min_prereq_grade': min([p[1] for p in prereq_performance]) if prereq_performance else 0.0,
                'max_prereq_grade': max([p[1] for p in prereq_performance]) if prereq_performance else 0.0,
            }
            
            cohort = service.cohort_stats.get(code, {})
            cohort_features = {
                'subject_pass_rate': cohort.get('pass_rate') if cohort.get('pass_rate') is not None else 0.5,
                'subject_avg_score': cohort.get('avg_score') if cohort.get('avg_score') is not None else 50.0,
                'subject_avg_gpa': cohort.get('avg_gpa', 2.0),
                'subject_total_students': cohort.get('total_students', 0),
            }
            
            batch_data.append({
                'student_features': student_features,
                'prereq_features': prereq_features,
                'cohort_features': cohort_features,
                'subject_code': code
            })
        
        # Test batch inference
        start_time = time.time()
        batch_results = service.ml_service.predict_batch(batch_data)
        ml_batch_time = time.time() - start_time
        
        # Test individual inference
        start_time = time.time()
        individual_results = []
        for data in batch_data:
            result = service.ml_service.predict(
                student_features=data['student_features'],
                prereq_features=data['prereq_features'],
                cohort_features=data['cohort_features'],
                subject_code=data['subject_code']
            )
            individual_results.append(result)
        ml_individual_time = time.time() - start_time
        
        print(f"ML Batch inference:       {ml_batch_time:.4f}s")
        print(f"ML Individual predictions: {ml_individual_time:.4f}s")
        
        if ml_batch_time < ml_individual_time:
            ml_speedup = ml_individual_time / ml_batch_time
            ml_improvement = ((ml_individual_time - ml_batch_time) / ml_individual_time) * 100
            print(f"✅ ML Speedup: {ml_speedup:.2f}x faster ({ml_improvement:.1f}% improvement)")
        
        print()
    
    print("="*70)
    print("✅ TEST 2 COMPLETE")
    print("="*70)


# ============================================================================
# TEST 3: API PERFORMANCE
# ============================================================================

def test_api_performance():
    """Test API endpoint performance"""
    
    print("\n" + "="*70)
    print("TEST 3: API PERFORMANCE")
    print("="*70)
    
    BASE_URL = "http://localhost:8000"
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend at {BASE_URL}")
        print(f"   Error: {e}")
        print("\n💡 Skipping API tests. Make sure backend is running: python run.py")
        return
    
    print("\nTesting public endpoints...\n")
    
    results = {}
    
    # Test endpoints
    endpoints = [
        ("Health Check", f"{BASE_URL}/api/health"),
        ("List Variants", f"{BASE_URL}/api/catalogue/variants"),
        ("Get Electives", f"{BASE_URL}/api/catalogue/variant/202301-normal/electives"),
        ("Get All Courses", f"{BASE_URL}/api/catalogue/variant/202301-normal/courses"),
    ]
    
    for name, url in endpoints:
        print(f"Testing: {name}")
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} | Time: {elapsed:.3f}s")
                results[name] = elapsed
            else:
                print(f"   ❌ Status: {response.status_code}")
                results[name] = None
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
            results[name] = None
    
    # Summary
    print("\n" + "-"*70)
    print("API PERFORMANCE SUMMARY")
    print("-"*70)
    
    for name, elapsed in results.items():
        if elapsed is not None:
            status = "🟢 FAST" if elapsed < 1.0 else "🟡 SLOW" if elapsed < 5.0 else "🔴 VERY SLOW"
            print(f"{status} {name:20s}: {elapsed:.3f}s")
        else:
            print(f"❌ {name:20s}: FAILED")
    
    print("\n" + "="*70)
    print("✅ TEST 3 COMPLETE")
    print("="*70)


# ============================================================================
# TEST 4: ACADEMIC PLANNER
# ============================================================================

def test_academic_planner():
    """Test academic planner with ML predictions"""
    
    print("\n" + "="*70)
    print("TEST 4: ACADEMIC PLANNER WITH ML PREDICTIONS")
    print("="*70)
    
    student_id = 2733926
    intake = "202301"
    entry_type = "normal"
    
    print(f"\nStudent ID: {student_id}")
    print(f"Variant: {intake}-{entry_type}")
    
    # Step 1: Load student data
    print("\nStep 1: Loading student data...")
    csv_service = get_csv_service()
    
    if not csv_service.is_available():
        print("❌ CSV service not available!")
        return
    
    completed_codes = csv_service.get_completed_subject_codes(student_id)
    if not completed_codes:
        print(f"❌ Student {student_id} not found!")
        return
    
    print(f"✅ Found {len(completed_codes)} completed subjects")
    
    # Step 2: Load program variant
    print("\nStep 2: Loading program variant...")
    variants = load_bcs_variants()
    variant_key = f"{intake}-{entry_type}"
    
    if variant_key not in variants:
        print(f"❌ Variant {variant_key} not found!")
        return
    
    variant = variants[variant_key]
    print(f"✅ Loaded variant: {variant_key}")
    
    # Step 3: Compute progress
    print("\nStep 3: Computing progress...")
    progress = variant.compute_progress(set(completed_codes))
    
    print(f"✅ Progress:")
    print(f"   Completed: {progress.completed_credits}/{progress.total_credits} credits")
    print(f"   Progress: {progress.percent_complete:.1f}%")
    print(f"   Core remaining: {len(progress.core_remaining)}")
    print(f"   Discipline electives remaining: {len(progress.discipline_elective_placeholders_remaining)}")
    
    # Step 4: Get elective options
    print("\nStep 4: Finding eligible electives...")
    elective_subjects = []
    
    all_placeholders = (
        progress.discipline_elective_placeholders_remaining + 
        progress.free_elective_placeholders_remaining
    )
    
    for placeholder_code in all_placeholders:
        if placeholder_code in variant.elective_groups:
            group = variant.elective_groups[placeholder_code]
            for course in group.options:
                prereqs_met = all(prereq in completed_codes for prereq in course.prerequisites)
                if prereqs_met and not course.is_placeholder:
                    elective_subjects.append({
                        'code': course.subject_code,
                        'name': course.subject_name,
                        'group': placeholder_code,
                    })
    
    print(f"✅ Found {len(elective_subjects)} eligible electives")
    
    if not elective_subjects:
        print("⚠️  No electives available")
        print("\n" + "="*70)
        print("✅ TEST 4 COMPLETE")
        print("="*70)
        return
    
    # Step 5: Get predictions
    print(f"\nStep 5: Running predictions for {len(elective_subjects)} electives...")
    start_time = time.time()
    
    prediction_service = get_prediction_service()
    elective_codes = [e['code'] for e in elective_subjects]
    report = prediction_service.predict_multiple_subjects(
        student_id=int(student_id),
        target_subject_codes=elective_codes
    )
    
    ml_time = time.time() - start_time
    print(f"✅ Predictions completed in {ml_time:.2f}s")
    
    # Display top recommendations
    top_recommendations = sorted(
        report.predictions,
        key=lambda x: x.ml_probability if x.ml_probability is not None else x.predicted_success_probability,
        reverse=True
    )[:10]
    
    print(f"\n🎯 TOP 10 RECOMMENDED ELECTIVES")
    print("-" * 70)
    
    for i, pred in enumerate(top_recommendations, 1):
        elective_info = next((e for e in elective_subjects if e['code'] == pred.subject_code), None)
        if elective_info:
            pass_prob = (pred.ml_probability or pred.predicted_success_probability) * 100
            print(f"\n{i}. {pred.subject_code} - {elective_info['name']}")
            print(f"   Pass Probability: {pass_prob:.1f}% | Risk: {pred.risk_level.upper()}")
    
    print("\n" + "="*70)
    print("✅ TEST 4 COMPLETE")
    print("="*70)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests"""
    
    print("\n" + "="*70)
    print("PATHFINDER COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("This suite tests:")
    print("  1. Hybrid Prediction System (ML + Rule-based)")
    print("  2. Batch Performance Optimization")
    print("  3. API Endpoint Performance")
    print("  4. Academic Planner with ML Integration")
    print("="*70)
    
    start_time = time.time()
    
    # Test ML service availability first
    test_ml_service_directly()
    
    # Run all tests
    test_hybrid_predictions()
    test_batch_performance()
    test_api_performance()
    test_academic_planner()
    
    # Final summary
    total_time = time.time() - start_time
    print("\n" + "="*70)
    print("🎉 ALL TESTS COMPLETED")
    print("="*70)
    print(f"Total execution time: {total_time:.2f} seconds")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
