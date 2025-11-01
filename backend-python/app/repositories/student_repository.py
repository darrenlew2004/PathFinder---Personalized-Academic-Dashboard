from typing import Optional, List
from uuid import UUID
from datetime import datetime
import logging
from app.models import Student, StudentCreate
from app.services.cassandra_service import cassandra_service
from passlib.hash import bcrypt

logger = logging.getLogger(__name__)


class StudentRepository:
    def __init__(self):
        self.session = cassandra_service.get_session()
        self.keyspace = "subjectplanning"
    
    def find_by_email(self, email: str) -> Optional[Student]:
        """Find student by email"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.students 
                WHERE email = %s 
                ALLOW FILTERING
            """
            result = self.session.execute(query, (email,))
            row = result.one()
            
            if row:
                return self._map_row_to_student(row)
            return None
        except Exception as e:
            logger.error(f"Error finding student by email: {str(e)}")
            return None
    
    def find_by_id(self, student_id: UUID) -> Optional[Student]:
        """Find student by ID"""
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
    
    def find_by_student_id(self, student_id: str) -> Optional[Student]:
        """Find student by student ID number"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.students 
                WHERE student_id = %s 
                ALLOW FILTERING
            """
            result = self.session.execute(query, (student_id,))
            row = result.one()
            
            if row:
                return self._map_row_to_student(row)
            return None
        except Exception as e:
            logger.error(f"Error finding student by student_id: {str(e)}")
            return None
    
    def create(self, student_data: StudentCreate) -> Student:
        """Create a new student"""
        try:
            # Hash password
            password_hash = bcrypt.hash(student_data.password)
            
            student = Student(
                student_id=student_data.student_id,
                name=student_data.name,
                email=student_data.email,
                password_hash=password_hash,
                gpa=student_data.gpa,
                semester=student_data.semester
            )
            
            query = f"""
                INSERT INTO {self.keyspace}.students 
                (id, student_id, name, email, password_hash, gpa, semester, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.session.execute(query, (
                student.id,
                student.student_id,
                student.name,
                student.email,
                student.password_hash,
                student.gpa,
                student.semester,
                student.created_at,
                student.updated_at
            ))
            
            logger.info(f"Created student: {student.email}")
            return student
        except Exception as e:
            logger.error(f"Error creating student: {str(e)}")
            raise
    
    def update(self, student: Student) -> Student:
        """Update an existing student"""
        try:
            student.updated_at = datetime.utcnow()
            
            query = f"""
                UPDATE {self.keyspace}.students 
                SET name = %s, gpa = %s, semester = %s, updated_at = %s
                WHERE id = %s
            """
            
            self.session.execute(query, (
                student.name,
                student.gpa,
                student.semester,
                student.updated_at,
                student.id
            ))
            
            logger.info(f"Updated student: {student.id}")
            return student
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            raise
    
    def delete(self, student_id: UUID) -> bool:
        """Delete a student"""
        try:
            query = f"""
                DELETE FROM {self.keyspace}.students 
                WHERE id = %s
            """
            self.session.execute(query, (student_id,))
            logger.info(f"Deleted student: {student_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting student: {str(e)}")
            return False
    
    def find_all(self) -> List[Student]:
        """Find all students"""
        try:
            query = f"SELECT * FROM {self.keyspace}.students"
            result = self.session.execute(query)
            return [self._map_row_to_student(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding all students: {str(e)}")
            return []
    
    def verify_password(self, student: Student, password: str) -> bool:
        """Verify student password"""
        return bcrypt.verify(password, student.password_hash)
    
    def _map_row_to_student(self, row) -> Student:
        """Map Cassandra row to Student model"""
        return Student(
            id=row.id,
            student_id=row.student_id,
            name=row.name,
            email=row.email,
            password_hash=row.password_hash,
            gpa=row.gpa,
            semester=row.semester,
            created_at=row.created_at,
            updated_at=row.updated_at
        )


# Singleton instance
student_repository = StudentRepository()
