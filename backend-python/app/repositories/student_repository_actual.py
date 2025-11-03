"""
Student Repository for ACTUAL Cassandra schema
Table: students (with 23 columns as per real schema)
"""

from typing import Optional, List
from uuid import UUID
import logging
from app.models.actual_models import Student, StudentCreate, StudentResponse
from app.services.cassandra_service import cassandra_service

logger = logging.getLogger(__name__)


class StudentRepositoryActual:
    def __init__(self):
        self.session = cassandra_service.get_session()
        self.keyspace = "subjectplanning"
    
    def find_by_id(self, student_id: int) -> Optional[Student]:
        """Find student by ID (int primary key)"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.students 
                WHERE id = %s
            """
            result = self.session.execute(query, (student_id,))
            row = result.one()
            
            if row:
                return self._map_row_to_student(row)
            return None
        except Exception as e:
            logger.error(f"Error finding student by id: {str(e)}")
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
        """Map Cassandra row to Student model"""
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
            qualifications=getattr(row, 'qualifications', None),  # Keep as-is (complex type)
            race=getattr(row, 'race', None),
            sem=getattr(row, 'sem', None),
            sponsorname=getattr(row, 'sponsorname', None),
            status=getattr(row, 'status', None),
            subjects=getattr(row, 'subjects', None),  # Keep as-is (complex type)
            year=getattr(row, 'year', None),
            yearonaverage=getattr(row, 'yearonaverage', None),
            yearonecgpa=getattr(row, 'yearonecgpa', None)
        )


# Singleton instance
student_repository_actual = StudentRepositoryActual()
