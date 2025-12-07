"""
Student Repository for Cassandra schema
Table: students (with 23 columns as per real schema)
"""

from typing import Optional, List
from uuid import UUID
import logging
from app.models import Student, StudentCreate, StudentResponse
from app.services.cassandra_service import cassandra_service

logger = logging.getLogger(__name__)


class StudentRepository:
    def __init__(self):
        self.session = cassandra_service.get_session()
        self.keyspace = "subjectplanning"
        # Prepare statements for better performance
        self._prepared_find_by_id = None
        # Cache for completed subject codes to avoid repeated parsing
        self._completed_codes_cache = {}
        # Cache for entire student objects (more aggressive)
        self._student_object_cache = {}
        self._cache_timestamps = {}
    
    def _get_prepared_find_by_id(self):
        """Lazy load prepared statement for find_by_id"""
        if self._prepared_find_by_id is None:
            query = f"SELECT * FROM {self.keyspace}.students WHERE id = ?"
            self._prepared_find_by_id = self.session.prepare(query)
        return self._prepared_find_by_id
    
    def find_by_id(self, student_id: int) -> Optional[Student]:
        """Find student by ID (int primary key) - uses prepared statement for speed with aggressive caching"""
        import time
        
        # Check object cache first (10 minute TTL)
        if student_id in self._student_object_cache:
            cached_time = self._cache_timestamps.get(student_id, 0)
            if time.time() - cached_time < 600:  # 10 minutes
                logger.info(f"Returning cached student object for {student_id}")
                return self._student_object_cache[student_id]
        
        try:
            logger.info(f"Querying Cassandra for student {student_id}...")
            prepared = self._get_prepared_find_by_id()
            # Reduced timeout to 5 seconds to fail faster
            result = self.session.execute(prepared, (student_id,), timeout=5.0)
            row = result.one()
            
            if row:
                student = self._map_row_to_student(row)
                # Cache the result
                self._student_object_cache[student_id] = student
                self._cache_timestamps[student_id] = time.time()
                # Limit cache size
                if len(self._student_object_cache) > 500:
                    oldest_keys = sorted(self._cache_timestamps.items(), key=lambda x: x[1])[:100]
                    for key, _ in oldest_keys:
                        self._student_object_cache.pop(key, None)
                        self._cache_timestamps.pop(key, None)
                logger.info(f"Student {student_id} fetched and cached from Cassandra")
                return student
            return None
        except Exception as e:
            logger.error(f"Error finding student by id {student_id}: {str(e)}")
            # Return cached data even if expired if Cassandra fails
            if student_id in self._student_object_cache:
                logger.warning(f"Cassandra failed, returning stale cache for student {student_id}")
                return self._student_object_cache[student_id]
            return None
    
    def find_by_ic(self, ic: str) -> Optional[Student]:
        """Find student by IC number"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.students 
                WHERE ic = %s 
                ALLOW FILTERING
            """
            result = self.session.execute(query, (ic,))
            row = result.one()
            
            if row:
                return self._map_row_to_student(row)
            return None
        except Exception as e:
            logger.error(f"Error finding student by IC: {str(e)}")
            return None
    
    def find_by_programme_code(self, programmecode: str) -> List[Student]:
        """Find all students in a programme"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.students 
                WHERE programmecode = %s 
                ALLOW FILTERING
            """
            result = self.session.execute(query, (programmecode,))
            return [self._map_row_to_student(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding students by programme: {str(e)}")
            return []
    
    def find_all(self, limit: int = 100) -> List[Student]:
        """Find all students (with limit)"""
        try:
            query = f"SELECT * FROM {self.keyspace}.students LIMIT %s"
            result = self.session.execute(query, (limit,))
            return [self._map_row_to_student(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding all students: {str(e)}")
            return []
    
    def create(self, student_data: StudentCreate) -> Student:
        """Create a new student"""
        try:
            student = Student(
                ic=student_data.ic,
                name=student_data.name,
                programmecode=student_data.programmecode,
                year=student_data.year,
                sem=student_data.sem,
                gender=student_data.gender,
                country=student_data.country
            )
            
            query = f"""
                INSERT INTO {self.keyspace}.students 
                (id, ic, name, programmecode, year, sem, gender, country)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.session.execute(query, (
                student.id,
                student.ic,
                student.name,
                student.programmecode,
                student.year,
                student.sem,
                student.gender,
                student.country
            ))
            
            logger.info(f"Created student: {student.ic}")
            return student
        except Exception as e:
            logger.error(f"Error creating student: {str(e)}")
            raise
    
    def update(self, student_id: int, updates: dict) -> Optional[Student]:
        """Update student fields"""
        try:
            # Build dynamic UPDATE query
            set_clauses = []
            values = []
            
            allowed_fields = [
                'name', 'programmecode', 'year', 'sem', 'status', 'gender',
                'country', 'cohort', 'overallcgpa', 'overallcavg', 'graduated'
            ]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return self.find_by_id(student_id)
            
            values.append(student_id)
            query = f"""
                UPDATE {self.keyspace}.students 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            
            self.session.execute(query, values)
            logger.info(f"Updated student: {student_id}")
            return self.find_by_id(student_id)
            
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            raise
    
    def delete(self, student_id: int) -> bool:
        """Delete a student"""
        try:
            query = f"DELETE FROM {self.keyspace}.students WHERE id = %s"
            self.session.execute(query, (student_id,))
            logger.info(f"Deleted student: {student_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting student: {str(e)}")
            return False
    
    def _map_row_to_student(self, row) -> Student:
        """Map Cassandra row to Student model.
        Note: some deployments store taken courses under column 'subject' (singular)
        instead of 'subjects'. We gracefully fall back to either.
        """
        subjects_value = getattr(row, 'subjects', None)
        if subjects_value is None:
            subjects_value = getattr(row, 'subject', None)

        return Student(
            id=row.id,
            program=getattr(row, 'program', None),
            awardclassification=getattr(row, 'awardclassification', None),
            broadsheetyear=getattr(row, 'broadsheetyear', None),
            cavg=getattr(row, 'cavg', None),
            cohort=getattr(row, 'cohort', None),
            country=getattr(row, 'country', None),
            finanicalaid=getattr(row, 'finanicalaid', None),
            gender=getattr(row, 'gender', None),
            graduated=getattr(row, 'graduated', None),
            ic=getattr(row, 'ic', None),
            name=getattr(row, 'name', None),
            overallcavg=getattr(row, 'overallcavg', None),
            overallcgpa=getattr(row, 'overallcgpa', None),
            programmecode=getattr(row, 'programmecode', None),
            qualifications=getattr(row, 'qualifications', None),
            race=getattr(row, 'race', None),
            sem=getattr(row, 'sem', None),
            sponsorname=getattr(row, 'sponsorname', None),
            status=getattr(row, 'status', None),
            subjects=subjects_value,
            year=getattr(row, 'year', None),
            yearonaverage=getattr(row, 'yearonaverage', None),
            yearonecgpa=getattr(row, 'yearonecgpa', None)
        )

    def get_completed_subject_codes(self, student_id: int) -> List[str]:
        """Extract completed subject codes from the student's stored subjects/subject column.

        Supports multiple storage formats:
        - List[Map]: each entry may contain keys like 'subjectcode'/'subject_code'/'code' and 'grade'/'result'/'status'
        - JSON string representing the above
        - Comma-separated string like "CODE:GRADE,CODE:GRADE"
        Filters out failing/withdrawn grades: {'F','FA','W'}.
        Returns an empty list if nothing can be parsed.
        Cached for performance.
        """
        # Check cache first
        if student_id in self._completed_codes_cache:
            return self._completed_codes_cache[student_id]
        
        try:
            student = self.find_by_id(student_id)
            if not student:
                return []

            raw = student.subjects
            if raw is None:
                # Attempt direct fetch of singular column if mapping didn't catch it
                prepared = self._get_prepared_find_by_id()
                row = self.session.execute(prepared, (student_id,)).one()
                if row is None:
                    return []
                raw = getattr(row, 'subjects', getattr(row, 'subject', None))

            fail_grades = {"F", "FA", "W"}
            codes: List[str] = []

            # Case 1: already a list-like of dicts/maps
            if isinstance(raw, list):
                for entry in raw:
                    try:
                        if isinstance(entry, dict):
                            # Fast path: use get() only once per key
                            code = entry.get('subjectcode') or entry.get('subject_code') or entry.get('code') or entry.get('subcode')
                            if code:
                                grade = entry.get('grade') or entry.get('result') or entry.get('status')
                                if grade is None or str(grade).upper() not in fail_grades:
                                    codes.append(str(code))
                        else:
                            # Unknown element type; skip safely
                            continue
                    except Exception:
                        continue
                # Cache and return (increased cache size)
                if len(self._completed_codes_cache) < 1000:
                    self._completed_codes_cache[student_id] = codes
                logger.info(f"Parsed {len(codes)} completed subjects for student {student_id}")
                return codes

            # Case 2: JSON string form
            if isinstance(raw, str):
                import json
                text = raw.strip()
                # Try JSON first
                try:
                    data = json.loads(text)
                    if isinstance(data, list):
                        for entry in data:
                            if isinstance(entry, dict):
                                code = entry.get('subjectcode') or entry.get('subject_code') or entry.get('code') or entry.get('subcode')
                                grade = entry.get('grade') or entry.get('result') or entry.get('status')
                                if code and (grade is None or str(grade).upper() not in fail_grades):
                                    codes.append(str(code))
                        # Cache and return
                        if len(self._completed_codes_cache) < 100:
                            self._completed_codes_cache[student_id] = codes
                        return codes
                except Exception:
                    pass

                # Fallback: parse CSV like "CODE:GRADE,CODE:GRADE" or just "CODE1,CODE2"
                try:
                    parts = [p.strip() for p in text.split(',') if p.strip()]
                    for p in parts:
                        if ':' in p:
                            code_part, grade_part = p.split(':', 1)
                            code = code_part.strip()
                            grade = grade_part.strip().upper()
                            if code and grade not in fail_grades:
                                codes.append(code)
                        else:
                            # Just a code with no grade info
                            if p:
                                codes.append(p)
                    # Cache and return
                    if len(self._completed_codes_cache) < 100:
                        self._completed_codes_cache[student_id] = codes
                    return codes
                except Exception:
                    return []

            # Unknown format
            return []
        except Exception as e:
            logger.error(f"Error extracting completed subject codes: {str(e)}")
            return []

    def get_subject_entries(self, student_id: int, *, dedup: bool = True, sort_desc: bool = True) -> List[dict]:
        """Parse the student's subjects/subject column into a normalized list of entries.

        Each returned dict may contain keys:
        - subjectcode, subjectname, grade, overallpercentage, attendancepercentage,
          courseworkpercentage, status, examyear, exammonth
        Unknown or missing fields are omitted.
        Supports list-of-dicts, JSON string, or CSV formats similar to get_completed_subject_codes.
        """
        try:
            student = self.find_by_id(student_id)
            if not student:
                return []

            raw = student.subjects
            if raw is None:
                prepared = self._get_prepared_find_by_id()
                row = self.session.execute(prepared, (student_id,)).one()
                if row is None:
                    return []
                raw = getattr(row, 'subjects', getattr(row, 'subject', None))

            entries: List[dict] = []

            def normalize_entry(entry: dict) -> dict:
                def pick(*keys):
                    for k in keys:
                        if k in entry and entry[k] is not None:
                            return entry[k]
                    return None

                return {
                    'subjectcode': pick('subjectcode', 'subject_code', 'code', 'subcode'),
                    'subjectname': pick('subjectname', 'name', 'subject_name'),
                    'grade': pick('grade', 'result', 'finalgrade'),
                    'overallpercentage': pick('overallpercentage', 'overall', 'overall_percentage', 'percentage'),
                    'attendancepercentage': pick('attendancepercentage', 'attendance', 'attendance_rate'),
                    'courseworkpercentage': pick('courseworkpercentage', 'coursework', 'coursework_rate'),
                    'status': pick('status', 'examstatus'),
                    'examyear': pick('examyear', 'year'),
                    'exammonth': pick('exammonth', 'month')
                }

            # Case 1: list of dicts
            if isinstance(raw, list):
                for e in raw:
                    if isinstance(e, dict):
                        norm = normalize_entry(e)
                        # discard entirely empty rows
                        if any(v is not None for v in norm.values()):
                            entries.append(norm)
                return self._post_process_entries(entries, dedup=dedup, sort_desc=sort_desc)

            # Case 2: JSON string
            if isinstance(raw, str):
                import json
                text = raw.strip()
                # Try JSON array first
                try:
                    data = json.loads(text)
                    if isinstance(data, list):
                        for e in data:
                            if isinstance(e, dict):
                                norm = normalize_entry(e)
                                if any(v is not None for v in norm.values()):
                                    entries.append(norm)
                        return self._post_process_entries(entries, dedup=dedup, sort_desc=sort_desc)
                except Exception:
                    pass

                # Fallback CSV: CODE:GRADE pairs or CODE only
                # We fabricate minimal entries from CSV tokens
                try:
                    parts = [p.strip() for p in text.split(',') if p.strip()]
                    for p in parts:
                        if ':' in p:
                            code_part, grade_part = p.split(':', 1)
                            entries.append({'subjectcode': code_part.strip(), 'grade': grade_part.strip()})
                        else:
                            entries.append({'subjectcode': p})
                    return self._post_process_entries(entries, dedup=dedup, sort_desc=sort_desc)
                except Exception:
                    return []

            return []
        except Exception as e:
            logger.error(f"Error parsing subjects column: {str(e)}")
            return []

    def _post_process_entries(self, entries: List[dict], *, dedup: bool, sort_desc: bool) -> List[dict]:
        """Optionally de-duplicate by subjectcode and sort by exam year/month.
        - dedup: keep the latest attempt per subjectcode based on (examyear, exammonth)
        - sort_desc: sort by (examyear, exammonth) descending
        """
        if not entries:
            return []

        processed = list(entries)

        if dedup:
            best_by_code: dict[str, dict] = {}
            for e in processed:
                code = e.get('subjectcode')
                if not code:
                    # Keep entries without code as-is
                    continue
                def ym(entry):
                    y = entry.get('examyear') or 0
                    m = entry.get('exammonth') or 0
                    try:
                        y = int(y)
                    except Exception:
                        y = 0
                    try:
                        m = int(m)
                    except Exception:
                        m = 0
                    return (y, m)

                cur_best = best_by_code.get(code)
                if cur_best is None or ym(e) >= ym(cur_best):
                    best_by_code[code] = e

            # Include non-coded entries too
            no_code = [e for e in processed if not e.get('subjectcode')]
            processed = list(best_by_code.values()) + no_code

        if sort_desc:
            def sort_key(e):
                y = e.get('examyear') or 0
                m = e.get('exammonth') or 0
                try:
                    y = int(y)
                except Exception:
                    y = 0
                try:
                    m = int(m)
                except Exception:
                    m = 0
                return (y, m)
            processed.sort(key=sort_key, reverse=True)

        return processed


# Singleton instance
student_repository = StudentRepository()
