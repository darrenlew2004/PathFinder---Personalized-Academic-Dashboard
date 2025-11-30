"""
Extract subjects column from Cassandra student table and store locally.
Cassandra schema: subjects is set<frozen<map<text, text>>>
When queried, 'subjects' is a Python set of dicts.
For each student, flatten this into one row per subject.
Output: pandas DataFrame with columns: student_id, subjectCode, subjectName, grade, etc.
"""

import sys
import os
import logging
from pathlib import Path

# Set up gevent for Cassandra driver (Python 3.13 compatibility)
import gevent.monkey
gevent.monkey.patch_all()

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cassandra_service import cassandra_service
from app.config import settings
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_subjects_from_cassandra() -> pd.DataFrame:
    """
    Extract all students and their subjects from Cassandra.
    Flatten the set<frozen<map<text, text>>> into individual rows.
    
    Returns:
        pandas DataFrame with one row per student-subject combination
    """
    logger.info("Starting subjects extraction from Cassandra...")
    
    # Get session
    session = cassandra_service.get_session()
    if not session:
        raise Exception("Failed to connect to Cassandra")
    
    keyspace = settings.CASSANDRA_KEYSPACE
    
    # Query first 20 students with subjects
    query = f"SELECT id, name, ic, programmecode, year, sem, subjects FROM {keyspace}.students LIMIT 20"
    logger.info(f"Executing query: {query}")
    
    result = session.execute(query)
    
    # Flatten subjects into rows
    flattened_data: List[Dict[str, Any]] = []
    student_count = 0
    subject_count = 0
    
    for row in result:
        student_count += 1
        student_id = row.id
        student_name = row.name
        student_ic = row.ic
        programme_code = row.programmecode
        year = row.year
        sem = row.sem
        subjects = row.subjects
        
        # Debug: log first few students to see what we're getting
        if student_count <= 3:
            logger.info(f"Student {student_count}: id={student_id}, name={student_name}, subjects type={type(subjects)}, subjects={subjects}")
        
        # Log progress every 100 students
        if student_count % 100 == 0:
            logger.info(f"Processed {student_count} students, extracted {subject_count} subject records")
        
        # Handle different subject formats
        if subjects is None:
            logger.debug(f"Student {id} has no subjects")
            continue
        
        # Convert set to list if needed
        if isinstance(subjects, set):
            subjects = list(subjects)
        
        # Process each subject
        if isinstance(subjects, list):
            for subject_entry in subjects:
                if isinstance(subject_entry, dict):
                    # Extract fields with various possible key names
                    subject_data = {
                        'id': student_id,
                        'student_name': student_name,
                        'student_ic': student_ic,
                        'programmecode': programme_code,
                        'student_year': year,
                        'student_sem': sem,
                        # Use EXACT key names from your data (case-sensitive!)
                        'subjectcode': subject_entry.get('subjectCode'),
                        'subjectname': subject_entry.get('subjectName'),
                        'grade': subject_entry.get('grade'),
                        'overallpercentage': subject_entry.get('overallPercentage'),
                        'attendancepercentage': subject_entry.get('attendancePercentage'),  # optional
                        'courseworkpercentage': subject_entry.get('courseworkPercentage'),
                        'exampercentage': subject_entry.get('examPercentage'),  # you had this in sample
                        'status': subject_entry.get('status'),
                        'examyear': subject_entry.get('examYear'),
                        'exammonth': subject_entry.get('examMonth'),
                    }
                    
                    # Convert numeric fields
                    for field in ['overallpercentage', 'attendancepercentage', 'courseworkpercentage']:
                        if subject_data[field] is not None:
                            try:
                                subject_data[field] = float(subject_data[field])
                            except (ValueError, TypeError):
                                subject_data[field] = None
                    
                    for field in ['examyear', 'exammonth', 'student_year', 'student_sem']:
                        if subject_data[field] is not None:
                            try:
                                subject_data[field] = int(subject_data[field])
                            except (ValueError, TypeError):
                                subject_data[field] = None
                    
                    flattened_data.append(subject_data)
                    subject_count += 1
    
    logger.info(f"Extraction complete: {student_count} students, {subject_count} subject records")
    
    # Create DataFrame
    df = pd.DataFrame(flattened_data)
    
    logger.info(f"Created DataFrame with shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    
    return df


def save_dataframe(df: pd.DataFrame, output_dir: str = "data"):
    """
    Save DataFrame to multiple formats (CSV, Parquet, Excel)
    
    Args:
        df: DataFrame to save
        output_dir: Directory to save files (default: 'data')
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as CSV with timestamp
    csv_file = output_path / f"subjects_flattened_{timestamp}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    logger.info(f"✅ Saved CSV: {csv_file}")
    
    # Also save a "latest" version without timestamp
    latest_csv = output_path / "subjects_flattened_latest.csv"
    df.to_csv(latest_csv, index=False, encoding='utf-8-sig')
    logger.info(f"✅ Saved latest CSV: {latest_csv}")
    
    return csv_file


def print_summary(df: pd.DataFrame):
    """Print summary statistics of the extracted data"""
    logger.info("\n" + "="*60)
    logger.info("DATA SUMMARY")
    logger.info("="*60)
    logger.info(f"Total rows (student-subject combinations): {len(df)}")
    
    if len(df) == 0:
        logger.warning("No data extracted! DataFrame is empty.")
        return
    
    logger.info(f"Unique students: {df['id'].nunique()}")
    logger.info(f"Unique subjects: {df['subjectcode'].nunique()}")
    logger.info(f"Unique programmes: {df['programmecode'].nunique()}")
    
    logger.info("\nColumn data types:")
    logger.info(str(df.dtypes))
    
    logger.info("\nMissing values:")
    logger.info(str(df.isnull().sum()))
    
    logger.info("\nGrade distribution:")
    if 'grade' in df.columns:
        logger.info(str(df['grade'].value_counts().head(20)))
    
    logger.info("\nTop 10 most taken subjects:")
    if 'subjectcode' in df.columns:
        logger.info(str(df['subjectcode'].value_counts().head(10)))
    
    logger.info("\nSample data (first 5 rows):")
    logger.info(str(df.head()))
    logger.info("="*60 + "\n")


def main():
    """Main execution function"""
    try:
        # Extract data
        df = extract_subjects_from_cassandra()
        
        # Print summary
        print_summary(df)
        
        # Save to files
        output_file = save_dataframe(df, output_dir="data")
        
        if len(df) > 0:
            logger.info(f"\n✅ Extraction complete! Data saved to: {output_file}")
            logger.info(f"   Total records: {len(df)}")
            logger.info(f"   Unique students: {df['id'].nunique()}")
            logger.info(f"   Unique subjects: {df['subjectcode'].nunique()}")
        else:
            logger.warning("\n⚠️ No data was extracted from the database!")
            logger.warning("   Check if the 'subjects' column contains data for these students.")
        
    except Exception as e:
        logger.error(f"❌ Error during extraction: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
