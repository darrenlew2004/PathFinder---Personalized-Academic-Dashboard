"""
Prepare ML Training Data from Cassandra CSV Exports

This script merges studentsTable.csv and subjectsTable.csv to create
a feature-rich dataset for Random Forest training.

Input files:
- studentsTable.csv: Student demographics and overall performance
- subjectsTable.csv: Individual subject records

Output:
- ml_training_data.csv: Feature-engineered dataset ready for ML training
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to import subject prediction service
sys.path.append(str(Path(__file__).parent.parent))
from app.services.subject_prediction_service import SUBJECT_PREREQUISITES, GRADE_POINTS


def load_data(data_dir):
    """Load the two CSV files from Cassandra"""
    print("Loading data from Cassandra exports...")
    
    # Load students table
    students_df = pd.read_csv(
        data_dir / 'studentsTable.csv',
        header=None,
        names=['id', 'programme', 'programmecode', 'yearonecgpa', 'overallcgpa', 
               'cohort', 'gender', 'financialaid']
    )
    
    # Load subjects table
    subjects_df = pd.read_csv(
        data_dir / 'subjectsTable.csv',
        header=None,
        names=['id', 'programmecode', 'subjectcode', 'subjectname', 'examyear', 
               'exammonth', 'status', 'attendancepercentage', 'courseworkpercentage',
               'exampercentage', 'grade', 'overallpercentage']
    )
    
    print(f"✓ Students: {len(students_df)} records, {students_df['id'].nunique()} unique")
    print(f"✓ Subjects: {len(subjects_df)} records")
    
    return students_df, subjects_df


def clean_data(students_df, subjects_df):
    """Clean and prepare data"""
    print("\nCleaning data...")
    
    # Replace 'null' strings with NaN
    students_df = students_df.replace('null', np.nan)
    subjects_df = subjects_df.replace('null', np.nan)
    
    # Convert numeric columns
    students_df['yearonecgpa'] = pd.to_numeric(students_df['yearonecgpa'], errors='coerce')
    students_df['overallcgpa'] = pd.to_numeric(students_df['overallcgpa'], errors='coerce')
    students_df['cohort'] = pd.to_numeric(students_df['cohort'], errors='coerce')
    
    subjects_df['examyear'] = pd.to_numeric(subjects_df['examyear'], errors='coerce')
    subjects_df['exammonth'] = pd.to_numeric(subjects_df['exammonth'], errors='coerce')
    subjects_df['courseworkpercentage'] = pd.to_numeric(subjects_df['courseworkpercentage'], errors='coerce')
    subjects_df['exampercentage'] = pd.to_numeric(subjects_df['exampercentage'], errors='coerce')
    subjects_df['overallpercentage'] = pd.to_numeric(subjects_df['overallpercentage'], errors='coerce')
    
    # Filter out non-graded subjects
    exclude_grades = ['P', 'EX', 'INC', 'W', '-', '']
    subjects_df = subjects_df[~subjects_df['grade'].isin(exclude_grades)]
    subjects_df = subjects_df[subjects_df['grade'].notna()]
    subjects_df = subjects_df[subjects_df['grade'].str.strip() != '']
    
    # Remove rows with missing critical data
    subjects_df = subjects_df[subjects_df['examyear'].notna()]
    subjects_df = subjects_df[subjects_df['exammonth'].notna()]
    
    print(f"✓ After cleaning: {len(subjects_df)} graded subject records")
    
    return students_df, subjects_df


def calculate_gpa(grades):
    """Calculate GPA from list of grades"""
    valid_gps = []
    for grade in grades:
        if pd.notna(grade) and grade in GRADE_POINTS:
            gp = GRADE_POINTS[grade]
            if gp is not None:
                valid_gps.append(gp)
    return np.mean(valid_gps) if valid_gps else 0.0


def calculate_prerequisite_features(student_id, subject_code, all_subjects_df, before_date):
    """Calculate prerequisite performance features"""
    prereqs = SUBJECT_PREREQUISITES.get(subject_code, [])
    
    if not prereqs:
        return {
            'num_prerequisites': 0,
            'num_prerequisites_completed': 0,
            'num_prerequisites_missing': 0,
            'avg_prereq_grade_points': 0.0,
            'weighted_prereq_gpa': 0.0,
            'min_prereq_grade': 0.0,
            'max_prereq_grade': 0.0
        }
    
    # Get student's subjects taken before target date
    student_subjects = all_subjects_df[all_subjects_df['id'] == student_id]
    before_subjects = student_subjects[
        (student_subjects['examyear'] < before_date[0]) |
        ((student_subjects['examyear'] == before_date[0]) & 
         (student_subjects['exammonth'] < before_date[1]))
    ]
    
    prereq_codes = [code for code, weight in prereqs]
    completed_prereqs = before_subjects[before_subjects['subjectcode'].isin(prereq_codes)]
    
    prereq_gps = []
    weighted_scores = []
    total_weight = 0.0
    
    for prereq_code, weight in prereqs:
        prereq_row = completed_prereqs[completed_prereqs['subjectcode'] == prereq_code]
        if len(prereq_row) > 0:
            grade = prereq_row.iloc[0]['grade']
            if grade in GRADE_POINTS and GRADE_POINTS[grade] is not None:
                gp = GRADE_POINTS[grade]
                prereq_gps.append(gp)
                weighted_scores.append(gp * weight)
                total_weight += weight
    
    return {
        'num_prerequisites': len(prereqs),
        'num_prerequisites_completed': len(prereq_gps),
        'num_prerequisites_missing': len(prereqs) - len(prereq_gps),
        'avg_prereq_grade_points': np.mean(prereq_gps) if prereq_gps else 0.0,
        'weighted_prereq_gpa': sum(weighted_scores) / total_weight if total_weight > 0 else 0.0,
        'min_prereq_grade': min(prereq_gps) if prereq_gps else 0.0,
        'max_prereq_grade': max(prereq_gps) if prereq_gps else 0.0
    }


def calculate_student_features(student_id, all_subjects_df, before_date):
    """Calculate student performance features up to a point in time"""
    student_subjects = all_subjects_df[all_subjects_df['id'] == student_id]
    before_subjects = student_subjects[
        (student_subjects['examyear'] < before_date[0]) |
        ((student_subjects['examyear'] == before_date[0]) & 
         (student_subjects['exammonth'] < before_date[1]))
    ]
    
    if len(before_subjects) == 0:
        return {
            'num_subjects_completed': 0,
            'current_gpa': 0.0,
            'gpa_trend_last_3': 0.0,
            'avg_coursework_percentage': 0.0,
            'avg_overall_percentage': 0.0,
            'num_fails': 0,
            'fail_rate': 0.0
        }
    
    # Calculate current GPA
    grades = before_subjects['grade'].tolist()
    current_gpa = calculate_gpa(grades)
    
    # GPA trend (last 3 vs previous 3)
    sorted_subjects = before_subjects.sort_values(['examyear', 'exammonth'])
    if len(sorted_subjects) >= 6:
        recent_3 = calculate_gpa(sorted_subjects.tail(3)['grade'].tolist())
        previous_3 = calculate_gpa(sorted_subjects.tail(6).head(3)['grade'].tolist())
        gpa_trend = recent_3 - previous_3
    else:
        gpa_trend = 0.0
    
    # Performance metrics
    avg_coursework = before_subjects['courseworkpercentage'].mean()
    avg_overall = before_subjects['overallpercentage'].mean()
    
    # Fail count
    failing_grades = ['D+', 'D', 'D-', 'E', 'F', 'F*']
    num_fails = before_subjects['grade'].isin(failing_grades).sum()
    fail_rate = num_fails / len(before_subjects) if len(before_subjects) > 0 else 0.0
    
    return {
        'num_subjects_completed': len(before_subjects),
        'current_gpa': current_gpa,
        'gpa_trend_last_3': gpa_trend,
        'avg_coursework_percentage': avg_coursework if pd.notna(avg_coursework) else 0.0,
        'avg_overall_percentage': avg_overall if pd.notna(avg_overall) else 0.0,
        'num_fails': num_fails,
        'fail_rate': fail_rate
    }


def calculate_subject_cohort_features(subject_code, all_subjects_df):
    """Calculate historical statistics for a subject"""
    subject_data = all_subjects_df[all_subjects_df['subjectcode'] == subject_code]
    
    if len(subject_data) == 0:
        return {
            'subject_pass_rate': 0.5,
            'subject_avg_score': 50.0,
            'subject_avg_gpa': 2.0,
            'subject_total_students': 0
        }
    
    # Pass rate (C or better)
    passing_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
    pass_rate = subject_data['grade'].isin(passing_grades).sum() / len(subject_data)
    
    # Average scores
    avg_score = subject_data['overallpercentage'].mean()
    avg_gpa = calculate_gpa(subject_data['grade'].tolist())
    
    return {
        'subject_pass_rate': pass_rate,
        'subject_avg_score': avg_score if pd.notna(avg_score) else 50.0,
        'subject_avg_gpa': avg_gpa,
        'subject_total_students': len(subject_data)
    }


def engineer_features(students_df, subjects_df):
    """Engineer features for ML training"""
    print("\nEngineering features for ML training...")
    
    # Calculate cohort statistics (one-time)
    print("Calculating subject cohort statistics...")
    subject_stats = {}
    unique_subjects = subjects_df['subjectcode'].unique()
    for idx, subject_code in enumerate(unique_subjects):
        if idx % 50 == 0:
            print(f"  Processing subject {idx}/{len(unique_subjects)}...")
        subject_stats[subject_code] = calculate_subject_cohort_features(subject_code, subjects_df)
    
    # Build training dataset
    print("\nEngineering features for each student-subject pair...")
    training_data = []
    
    for idx, row in subjects_df.iterrows():
        if idx % 500 == 0:
            print(f"  Processing record {idx}/{len(subjects_df)}...")
        
        student_id = row['id']
        subject_code = row['subjectcode']
        exam_date = (row['examyear'], row['exammonth'])
        
        # Get student demographic info
        student_info = students_df[students_df['id'] == student_id].iloc[0] if len(students_df[students_df['id'] == student_id]) > 0 else None
        
        # Target variable: Did student pass? (C or better)
        passing_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        passed = 1 if row['grade'] in passing_grades else 0
        
        # Get grade points
        grade_points = GRADE_POINTS.get(row['grade'], 0.0)
        if grade_points is None:
            grade_points = 0.0
        
        # Calculate features
        student_features = calculate_student_features(student_id, subjects_df, exam_date)
        prereq_features = calculate_prerequisite_features(student_id, subject_code, subjects_df, exam_date)
        cohort_features = subject_stats.get(subject_code, {})
        
        # Combine all features
        record = {
            # Identifiers
            'student_id': student_id,
            'subject_code': subject_code,
            'subject_name': row['subjectname'],
            'exam_year': row['examyear'],
            'exam_month': row['exammonth'],
            
            # Target variables
            'passed': passed,
            'grade': row['grade'],
            'grade_points': grade_points,
            'overall_percentage': row['overallpercentage'] if pd.notna(row['overallpercentage']) else 0.0,
            
            # Student demographic features
            'programme_code': student_info['programmecode'] if student_info is not None else '',
            'gender': student_info['gender'] if student_info is not None else '',
            'cohort': student_info['cohort'] if student_info is not None else 0,
            'has_financial_aid': 1 if (student_info is not None and pd.notna(student_info['financialaid']) and student_info['financialaid'] != '') else 0,
            
            # Student performance features
            **student_features,
            
            # Prerequisite features
            **prereq_features,
            
            # Subject cohort features
            **cohort_features,
            
            # Additional features
            'coursework_percentage': row['courseworkpercentage'] if pd.notna(row['courseworkpercentage']) else 0.0,
            'exam_percentage': row['exampercentage'] if pd.notna(row['exampercentage']) else 0.0,
        }
        
        training_data.append(record)
    
    return pd.DataFrame(training_data)


def main():
    """Main execution"""
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Check input files
    if not (data_dir / 'studentsTable.csv').exists():
        print("ERROR: studentsTable.csv not found!")
        return
    if not (data_dir / 'subjectsTable.csv').exists():
        print("ERROR: subjectsTable.csv not found!")
        return
    
    # Load data
    students_df, subjects_df = load_data(data_dir)
    
    # Clean data
    students_df, subjects_df = clean_data(students_df, subjects_df)
    
    # Engineer features
    training_df = engineer_features(students_df, subjects_df)
    
    # Save output
    output_file = data_dir / 'ml_training_data.csv'
    print(f"\nSaving to {output_file}...")
    training_df.to_csv(output_file, index=False)
    
    # Summary statistics
    print("\n" + "="*70)
    print("ML TRAINING DATA EXTRACTION COMPLETE!")
    print("="*70)
    print(f"Total records: {len(training_df):,}")
    print(f"Unique students: {training_df['student_id'].nunique():,}")
    print(f"Unique subjects: {training_df['subject_code'].nunique():,}")
    print(f"\nClass distribution:")
    print(f"  Passed (grade ≥ C): {training_df['passed'].sum():,} ({training_df['passed'].mean()*100:.1f}%)")
    print(f"  Failed (grade < C): {(training_df['passed'] == 0).sum():,} ({(1-training_df['passed'].mean())*100:.1f}%)")
    print(f"\nFeatures extracted: {len(training_df.columns)}")
    print(f"\nOutput saved to: {output_file}")
    print("\nNext step: Train Random Forest model")
    print("="*70)


if __name__ == "__main__":
    main()
