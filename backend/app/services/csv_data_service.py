"""
CSV Fallback Service - Fast local data access when Cassandra is slow
"""
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
import json
import logging

logger = logging.getLogger(__name__)


class CSVDataService:
    """Service to read student data from local CSV files when Cassandra is slow"""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.students_cache: Dict[int, Dict] = {}
        self._load_data()
    
    def _load_data(self):
        """Load student data from CSV"""
        try:
            csv_path = Path(__file__).parent.parent.parent / 'data' / 'subjectplanning_students.csv'
            if csv_path.exists():
                logger.info(f"Loading student data from CSV: {csv_path}")
                # CSV has no header, columns are: student_id, subjects_json
                self.df = pd.read_csv(csv_path, header=None, names=['id', 'subjects'])
                logger.info(f"Loaded {len(self.df)} students from CSV")
            else:
                logger.warning(f"CSV file not found: {csv_path}")
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
    
    def get_student_by_id(self, student_id) -> Optional[Dict]:
        """Get student data by ID from CSV"""
        # Convert to int if string
        if isinstance(student_id, str):
            student_id = int(student_id)
        
        # Check cache first
        if student_id in self.students_cache:
            return self.students_cache[student_id]
        
        if self.df is None:
            return None
        
        try:
            # Find student in dataframe
            student_rows = self.df[self.df['id'] == student_id]
            
            if len(student_rows) == 0:
                logger.warning(f"Student {student_id} not found in CSV")
                return None
            
            row = student_rows.iloc[0]
            
            # Parse the subjects column (it's a Java-like string format)
            subjects_raw = row['subjects']
            subjects = []
            
            if pd.notna(subjects_raw) and isinstance(subjects_raw, str):
                try:
                    # The CSV has Java/Groovy format: [{key=value, key=value}]
                    # Parse it safely
                    import re
                    
                    # Extract all {subject_data} blocks
                    subject_blocks = re.findall(r'\{([^}]+)\}', subjects_raw)
                    
                    for block in subject_blocks:
                        subject_dict = {}
                        # Split by comma, but handle spaces in values
                        pairs = re.findall(r'(\w+)=([^,]*?)(?:,|$)', block + ',')
                        for key, value in pairs:
                            subject_dict[key.strip()] = value.strip()
                        
                        if subject_dict:
                            subjects.append(subject_dict)
                    
                    logger.debug(f"Parsed {len(subjects)} subjects for student {student_id}")
                except Exception as e:
                    logger.error(f"Error parsing subjects for student {student_id}: {e}")
                    subjects = []
            
            student_data = {
                'id': int(row['id']),
                'subjects': subjects
            }
            
            # Cache it
            self.students_cache[student_id] = student_data
            
            logger.info(f"Loaded student {student_id} from CSV with {len(subjects)} subjects")
            return student_data
            
        except Exception as e:
            logger.error(f"Error getting student {student_id} from CSV: {e}")
            return None
    
    def get_completed_subject_codes(self, student_id) -> List[str]:
        """Get list of completed subject codes for a student"""
        # Convert to int if string
        if isinstance(student_id, str):
            student_id = int(student_id)
        student = self.get_student_by_id(student_id)
        if not student:
            return []
        
        fail_grades = {'F', 'F*', 'FA', 'W', 'INC', '-'}
        codes = []
        
        subjects = student.get('subjects', [])
        for subject in subjects:
            if isinstance(subject, dict):
                code = subject.get('subjectCode') or subject.get('subjectcode')
                grade = subject.get('grade')
                
                if code and (not grade or str(grade).upper() not in fail_grades):
                    codes.append(str(code))
        
        return codes
    
    def is_available(self) -> bool:
        """Check if CSV data is loaded"""
        return self.df is not None


# Singleton instance
_csv_service: Optional[CSVDataService] = None

def get_csv_service() -> CSVDataService:
    """Get or create CSV service singleton"""
    global _csv_service
    if _csv_service is None:
        _csv_service = CSVDataService()
    return _csv_service
