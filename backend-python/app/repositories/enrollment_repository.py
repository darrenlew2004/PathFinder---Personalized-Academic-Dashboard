from typing import Optional, List
from uuid import UUID
import logging
from app.models import Enrollment, CourseStatus
from app.services.cassandra_service import cassandra_service

logger = logging.getLogger(__name__)


class EnrollmentRepository:
    def __init__(self):
        self.session = cassandra_service.get_session()
        self.keyspace = "subjectplanning"
    
    def find_by_id(self, enrollment_id: UUID) -> Optional[Enrollment]:
        """Find enrollment by ID"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.enrollments 
                WHERE id = %s
            """
            result = self.session.execute(query, (enrollment_id,))
            row = result.one()
            
            if row:
                return self._map_row_to_enrollment(row)
            return None
        except Exception as e:
            logger.error(f"Error finding enrollment by id: {str(e)}")
            return None
    
    def find_by_student_id(self, student_id: UUID) -> List[Enrollment]:
        """Find all enrollments for a student"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.enrollments 
                WHERE student_id = %s 
                ALLOW FILTERING
            """
            result = self.session.execute(query, (student_id,))
            return [self._map_row_to_enrollment(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding enrollments by student_id: {str(e)}")
            return []
    
    def find_by_course_id(self, course_id: UUID) -> List[Enrollment]:
        """Find all enrollments for a course"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.enrollments 
                WHERE course_id = %s 
                ALLOW FILTERING
            """
            result = self.session.execute(query, (course_id,))
            return [self._map_row_to_enrollment(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding enrollments by course_id: {str(e)}")
            return []
    
    def find_current_enrollments(self, student_id: UUID) -> List[Enrollment]:
        """Find current (enrolled) courses for a student"""
        all_enrollments = self.find_by_student_id(student_id)
        return [e for e in all_enrollments if e.status == CourseStatus.ENROLLED]
    
    def find_completed_enrollments(self, student_id: UUID) -> List[Enrollment]:
        """Find completed courses for a student"""
        all_enrollments = self.find_by_student_id(student_id)
        return [e for e in all_enrollments if e.status == CourseStatus.COMPLETED]
    
    def create(self, enrollment: Enrollment) -> Enrollment:
        """Create a new enrollment"""
        try:
            query = f"""
                INSERT INTO {self.keyspace}.enrollments 
                (id, student_id, course_id, semester, grade, status, attendance_rate, enrolled_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.session.execute(query, (
                enrollment.id,
                enrollment.student_id,
                enrollment.course_id,
                enrollment.semester,
                enrollment.grade,
                enrollment.status.value,
                enrollment.attendance_rate,
                enrollment.enrolled_at,
                enrollment.completed_at
            ))
            
            logger.info(f"Created enrollment: {enrollment.id}")
            return enrollment
        except Exception as e:
            logger.error(f"Error creating enrollment: {str(e)}")
            raise
    
    def update(self, enrollment: Enrollment) -> Enrollment:
        """Update an existing enrollment"""
        try:
            query = f"""
                UPDATE {self.keyspace}.enrollments 
                SET grade = %s, status = %s, attendance_rate = %s, completed_at = %s
                WHERE id = %s
            """
            
            self.session.execute(query, (
                enrollment.grade,
                enrollment.status.value,
                enrollment.attendance_rate,
                enrollment.completed_at,
                enrollment.id
            ))
            
            logger.info(f"Updated enrollment: {enrollment.id}")
            return enrollment
        except Exception as e:
            logger.error(f"Error updating enrollment: {str(e)}")
            raise
    
    def delete(self, enrollment_id: UUID) -> bool:
        """Delete an enrollment"""
        try:
            query = f"""
                DELETE FROM {self.keyspace}.enrollments 
                WHERE id = %s
            """
            self.session.execute(query, (enrollment_id,))
            logger.info(f"Deleted enrollment: {enrollment_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting enrollment: {str(e)}")
            return False
    
    def _map_row_to_enrollment(self, row) -> Enrollment:
        """Map Cassandra row to Enrollment model"""
        return Enrollment(
            id=row.id,
            student_id=row.student_id,
            course_id=row.course_id,
            semester=row.semester,
            grade=row.grade,
            status=CourseStatus(row.status),
            attendance_rate=row.attendance_rate,
            enrolled_at=row.enrolled_at,
            completed_at=row.completed_at
        )


# Singleton instance
enrollment_repository = EnrollmentRepository()
