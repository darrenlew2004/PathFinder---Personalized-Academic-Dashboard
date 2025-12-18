"""
Test script to compare performance of batch inference vs individual predictions
"""
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.subject_prediction_service import get_prediction_service


def test_performance():
    """Compare batch vs individual prediction performance"""
    
    service = get_prediction_service()
    
    if service.df is None:
        print("❌ Data not loaded!")
        return
    
    # Test parameters
    test_student_id = 9897587
    test_subjects = ['CSC3206', 'NET2201', 'CSC3044', 'SEC3024', 'CSC3034']
    
    print("=" * 70)
    print("Performance Test: Batch Inference vs Individual Predictions")
    print("=" * 70)
    print(f"Student ID: {test_student_id}")
    print(f"Subjects: {', '.join(test_subjects)}")
    print()
    
    # Clear caches for fair comparison
    if hasattr(service, '_student_cache'):
        service._student_cache.clear()
    if hasattr(service, '_student_perf_cache'):
        service._student_perf_cache.clear()
    
    # Test 1: Batch inference (optimized with caching)
    print("🚀 Test 1: Batch Inference (with caching)")
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
    print("🐌 Test 2: Individual Predictions (no batch)")
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
    print("=" * 70)
    print("📈 Performance Comparison")
    print("=" * 70)
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
    print("=" * 70)
    print("🧠 Cache Effectiveness Test")
    print("=" * 70)
    
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
        print("=" * 70)
        print("🤖 ML Model: Batch vs Individual Inference")
        print("=" * 70)
        
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
    
    print("=" * 70)
    print("✅ Performance test completed!")
    print("=" * 70)


if __name__ == '__main__':
    test_performance()
