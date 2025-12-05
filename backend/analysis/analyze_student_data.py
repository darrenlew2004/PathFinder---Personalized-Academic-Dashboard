import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Load the flattened data
df = pd.read_csv('data/flattened_students_subjects.csv')

print("="*80)
print("STUDENT SUBJECT DATA ANALYTICS")
print("="*80)
print(f"\nTotal Records: {len(df)}")
print(f"Unique Students: {df['student_id'].nunique()}")
print(f"Unique Subjects: {df['subject_code'].nunique()}")

# Clean up the data
# Remove records with no grade or special grades
grades_to_analyze = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'F*', 'F**']
df_graded = df[df['grade'].isin(grades_to_analyze)].copy()

print(f"Records with letter grades: {len(df_graded)}")

# =============================================================================
# 1. GRADE DISTRIBUTION
# =============================================================================
print("\n" + "="*80)
print("1. GRADE DISTRIBUTION")
print("="*80)

grade_dist = df_graded['grade'].value_counts().sort_index()
print("\nGrade Counts:")
print(grade_dist.to_string())

print("\nGrade Percentages:")
grade_pct = (grade_dist / len(df_graded) * 100).round(2)
for grade, pct in grade_pct.items():
    print(f"  {grade}: {pct}%")

# Calculate pass rate (grades better than F)
pass_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-']
pass_count = df_graded[df_graded['grade'].isin(pass_grades)].shape[0]
overall_pass_rate = (pass_count / len(df_graded) * 100)
print(f"\nOverall Pass Rate: {overall_pass_rate:.2f}%")

# =============================================================================
# 2. TOP SUBJECTS BY ENROLLMENT
# =============================================================================
print("\n" + "="*80)
print("2. TOP SUBJECTS BY ENROLLMENT")
print("="*80)

subject_enrollment = df.groupby(['subject_code', 'subject_name']).size().reset_index(name='enrollment')
subject_enrollment = subject_enrollment.sort_values('enrollment', ascending=False)

print("\nTop 20 Subjects by Enrollment:")
for idx, row in subject_enrollment.head(20).iterrows():
    print(f"  {row['subject_code']:20s} - {row['subject_name']:50s}: {row['enrollment']:3d} students")

# =============================================================================
# 3. PASS RATE BY SUBJECT
# =============================================================================
print("\n" + "="*80)
print("3. PASS RATE BY SUBJECT")
print("="*80)

# Calculate pass rate for each subject
subject_stats = df_graded.groupby(['subject_code', 'subject_name']).agg({
    'grade': ['count', lambda x: (x.isin(pass_grades)).sum()]
}).reset_index()
subject_stats.columns = ['subject_code', 'subject_name', 'total_students', 'passed_students']
subject_stats['pass_rate'] = (subject_stats['passed_students'] / subject_stats['total_students'] * 100).round(2)
subject_stats = subject_stats.sort_values('pass_rate', ascending=True)

# Only show subjects with at least 5 students
subject_stats_filtered = subject_stats[subject_stats['total_students'] >= 5]

print(f"\nSubjects with Lowest Pass Rates (min 5 students):")
for idx, row in subject_stats_filtered.head(15).iterrows():
    print(f"  {row['subject_code']:20s} - {row['subject_name']:50s}")
    print(f"    Pass Rate: {row['pass_rate']:6.2f}% ({row['passed_students']}/{row['total_students']})")

print(f"\nSubjects with Highest Pass Rates (min 5 students):")
for idx, row in subject_stats_filtered.tail(15).iterrows():
    print(f"  {row['subject_code']:20s} - {row['subject_name']:50s}")
    print(f"    Pass Rate: {row['pass_rate']:6.2f}% ({row['passed_students']}/{row['total_students']})")

# =============================================================================
# 4. STUDENT PERFORMANCE OVER TIME
# =============================================================================
print("\n" + "="*80)
print("4. STUDENT PERFORMANCE OVER TIME")
print("="*80)

# Create a year-month column for time series analysis
df_graded_time = df_graded.copy()
df_graded_time['year_month'] = df_graded_time['exam_year'].astype(str) + '-' + df_graded_time['exam_month'].astype(str).str.zfill(2)

# Convert overall_percentage to numeric (handling empty strings)
df_graded_time['overall_percentage'] = pd.to_numeric(df_graded_time['overall_percentage'], errors='coerce')

# Calculate average performance by time period
performance_over_time = df_graded_time.groupby('year_month').agg({
    'overall_percentage': 'mean',
    'student_id': 'count',
    'grade': lambda x: (x.isin(pass_grades)).sum()
}).reset_index()
performance_over_time.columns = ['year_month', 'avg_percentage', 'total_exams', 'passed']
performance_over_time['pass_rate'] = (performance_over_time['passed'] / performance_over_time['total_exams'] * 100).round(2)
performance_over_time = performance_over_time.sort_values('year_month')

print("\nPerformance Trends by Exam Period:")
print(f"{'Period':<15} {'Avg %':<10} {'Total Exams':<15} {'Pass Rate':<10}")
print("-" * 50)
for idx, row in performance_over_time.iterrows():
    if pd.notna(row['avg_percentage']):
        print(f"{row['year_month']:<15} {row['avg_percentage']:>6.2f}%    {row['total_exams']:>5} exams     {row['pass_rate']:>6.2f}%")

# Calculate grade progression by year
print("\n\nGrade Distribution by Year:")
df_graded_time['exam_year'] = df_graded_time['exam_year'].astype(int)
year_grades = pd.crosstab(df_graded_time['exam_year'], df_graded_time['grade'], normalize='index') * 100

print(year_grades.round(2).to_string())

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

# Calculate average performance by grade category
grade_to_points = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'D-': 0.7,
    'F': 0.0, 'F*': 0.0, 'F**': 0.0
}

df_graded['grade_points'] = df_graded['grade'].map(grade_to_points)
avg_gpa = df_graded['grade_points'].mean()

print(f"\nAverage GPA: {avg_gpa:.2f}")
print(f"Median Grade: {df_graded['grade'].mode()[0]}")

# Most common subjects
print(f"\nMost Enrolled Subject: {subject_enrollment.iloc[0]['subject_name']} ({subject_enrollment.iloc[0]['enrollment']} students)")

# Best performing subject
best_subject = subject_stats_filtered.iloc[-1]
print(f"Highest Pass Rate Subject: {best_subject['subject_name']} ({best_subject['pass_rate']:.1f}%)")

# Worst performing subject
worst_subject = subject_stats_filtered.iloc[0]
print(f"Lowest Pass Rate Subject: {worst_subject['subject_name']} ({worst_subject['pass_rate']:.1f}%)")

print("\n" + "="*80)
print("Analytics complete! Data saved to: data/flattened_students_subjects.csv")
print("="*80)

# Optionally save the analytics results
subject_stats.to_csv('data/subject_pass_rates.csv', index=False)
subject_enrollment.to_csv('data/subject_enrollment.csv', index=False)
performance_over_time.to_csv('data/performance_over_time.csv', index=False)

print("\nAdditional files created:")
print("  - data/subject_pass_rates.csv")
print("  - data/subject_enrollment.csv")
print("  - data/performance_over_time.csv")
