"""
Test Academic Planner functionality with ML predictions for a specific student
"""
import sys
from pathlib import Path
import time

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.csv_data_service import get_csv_service
from app.catalog.bcs_programs import load_bcs_variants
from app.services.subject_prediction_service import get_prediction_service
from app.catalog.program_catalog_models import RiskEngine

def test_academic_planner(student_id: int, intake: str = "202301", entry_type: str = "normal"):
    """Test academic planner with ML predictions for a specific student"""
    print(f"\n{'='*70}")
    print(f"Testing Academic Planner with ML Predictions for Student {student_id}")
    print(f"Variant: {intake}-{entry_type}")
    print(f"{'='*70}\n")
    
    # Step 1: Load student data from CSV
    print("Step 1: Loading student data from CSV...")
    csv_service = get_csv_service()
    
    if not csv_service.is_available():
        print("❌ CSV service not available!")
        return
    
    completed_codes = csv_service.get_completed_subject_codes(student_id)
    if not completed_codes:
        print(f"❌ Student {student_id} not found in CSV!")
        return
    
    print(f"✅ Found {len(completed_codes)} completed subjects")
    print(f"   Sample codes: {completed_codes[:5]}")
    
    # Step 2: Load program variant
    print("\nStep 2: Loading program variant...")
    variants = load_bcs_variants()
    variant_key = f"{intake}-{entry_type}"
    
    if variant_key not in variants:
        print(f"❌ Variant {variant_key} not found!")
        print(f"   Available variants: {list(variants.keys())}")
        return
    
    variant = variants[variant_key]
    print(f"✅ Loaded variant: {variant_key}")
    
    # Step 3: Compute progress
    print("\nStep 3: Computing progress...")
    progress = variant.compute_progress(set(completed_codes))
    
    print(f"✅ Progress computed:")
    print(f"   Completed credits: {progress.completed_credits}/{progress.total_credits}")
    print(f"   Outstanding credits: {progress.outstanding_credits}")
    print(f"   Progress: {progress.percent_complete:.1f}%")
    print(f"   Core remaining: {len(progress.core_remaining)} subjects")
    print(f"   Discipline electives remaining: {len(progress.discipline_elective_placeholders_remaining)} placeholders")
    print(f"   Free electives remaining: {len(progress.free_elective_placeholders_remaining)} placeholders")
    
    if progress.core_remaining:
        print(f"\n   Core subjects to complete:")
        for code in progress.core_remaining[:5]:
            print(f"      - {code}")
        if len(progress.core_remaining) > 5:
            print(f"      ... and {len(progress.core_remaining) - 5} more")
    
    # Step 4: Get elective options with prerequisites
    print("\nStep 4: Finding elective options...")
    elective_subjects = []
    
    # Collect all elective placeholders
    all_placeholders = (
        progress.discipline_elective_placeholders_remaining + 
        progress.free_elective_placeholders_remaining
    )
    
    # Get actual course options for each placeholder
    for placeholder_code in all_placeholders:
        if placeholder_code in variant.elective_groups:
            group = variant.elective_groups[placeholder_code]
            for course in group.options:
                # Check if prerequisites are met
                prereqs_met = all(prereq in completed_codes for prereq in course.prerequisites)
                if prereqs_met and not course.is_placeholder:
                    elective_subjects.append({
                        'code': course.subject_code,
                        'name': course.subject_name,
                        'group': placeholder_code,
                        'prerequisites': course.prerequisites
                    })
    
    print(f"✅ Found {len(elective_subjects)} eligible elective courses")
    
    if not elective_subjects:
        print("\n⚠️  No electives available (all have unmet prerequisites or are placeholders)")
        print(f"\n{'='*70}")
        print("✅ Academic Planner test completed!")
        print(f"{'='*70}\n")
        return
    
    # Step 5: Get ML predictions for electives
    print(f"\nStep 5: Running ML predictions for {len(elective_subjects)} elective courses...")
    start_time = time.time()
    
    prediction_service = get_prediction_service()
    elective_codes = [e['code'] for e in elective_subjects]
    report = prediction_service.predict_multiple_subjects(
        student_id=int(student_id),
        target_subject_codes=elective_codes
    )
    predictions = report.predictions
    
    ml_time = time.time() - start_time
    print(f"✅ ML predictions completed in {ml_time:.2f} seconds")
    
    # Step 6: Display predictions sorted by pass probability
    print("\nStep 6: Analyzing predictions with prerequisite filtering...")
    
    # Get top 10 recommendations based on ML predictions
    top_recommendations = sorted(
        predictions,
        key=lambda x: x.ml_probability if x.ml_probability is not None else 0,
        reverse=True
    )[:10]
    
    print(f"\n{'='*70}")
    print("🎯 TOP 10 RECOMMENDED ELECTIVES (with Prerequisites Check)")
    print(f"{'='*70}")
    
    for i, pred in enumerate(top_recommendations, 1):
        code = pred.subject_code
        # Find the elective info
        elective_info = next((e for e in elective_subjects if e['code'] == code), None)
        
        if elective_info:
            pass_prob = (pred.ml_probability or pred.predicted_success_probability) * 100
            risk_level = pred.risk_level
            method = pred.prediction_method
            
            prereqs_str = ", ".join(elective_info['prerequisites']) if elective_info['prerequisites'] else "None"
            
            print(f"\n{i}. {code} - {elective_info['name']}")
            print(f"   Group: {elective_info['group']}")
            print(f"   Pass Probability: {pass_prob:.1f}% ({method})")
            print(f"   Risk Level: {risk_level.upper()}")
            print(f"   Prerequisites: {prereqs_str}")
            if pred.recommendation:
                print(f"   📝 {pred.recommendation}")
    
    print(f"\n{'='*70}")
    print("✅ Academic Planner with ML Predictions completed successfully!")
    print(f"   Total time: {time.time() - start_time + ml_time:.2f} seconds")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    # Get student ID from command line or use default
    student_id = int(sys.argv[1]) if len(sys.argv) > 1 else 2733926
    intake = sys.argv[2] if len(sys.argv) > 2 else "202301"
    entry_type = sys.argv[3] if len(sys.argv) > 3 else "normal"
    
    test_academic_planner(student_id, intake, entry_type)
