from typing import Optional, List
from uuid import UUID
import logging
from app.models import Course
from app.services.cassandra_service import cassandra_service

logger = logging.getLogger(__name__)


class CourseRepository:
    def __init__(self):
        self.session = cassandra_service.get_session()
        self.keyspace = "subjectplanning"
    
    def find_by_id(self, course_id: UUID) -> Optional[Course]:
        """Find course by ID"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.courses 
                WHERE id = %s
            """
            result = self.session.execute(query, (course_id,))
            row = result.one()
            
            if row:
                return self._map_row_to_course(row)
            return None
        except Exception as e:
            logger.error(f"Error finding course by id: {str(e)}")
            return None
    
    def find_by_course_code(self, course_code: str) -> Optional[Course]:
        """Find course by course code"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.courses 
                WHERE course_code = %s 
                ALLOW FILTERING
            """
            result = self.session.execute(query, (course_code,))
            row = result.one()
            
            if row:
                return self._map_row_to_course(row)
            return None
        except Exception as e:
            logger.error(f"Error finding course by code: {str(e)}")
            return None
    
    def find_all(self) -> List[Course]:
        """Find all courses"""
        try:
            query = f"SELECT * FROM {self.keyspace}.courses"
            result = self.session.execute(query)
            return [self._map_row_to_course(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding all courses: {str(e)}")
            return []
    
    def create(self, course: Course) -> Course:
        """Create a new course"""
        try:
            query = f"""
                INSERT INTO {self.keyspace}.courses 
                (id, course_code, course_name, credits, difficulty, prerequisites, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.session.execute(query, (
                course.id,
                course.course_code,
                course.course_name,
                course.credits,
                course.difficulty,
                course.prerequisites,
                course.description,
                course.created_at
            ))
            
            logger.info(f"Created course: {course.course_code}")
            return course
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            raise
    
    def update(self, course: Course) -> Course:
        """Update an existing course"""
        try:
            query = f"""
                UPDATE {self.keyspace}.courses 
                SET course_name = %s, credits = %s, difficulty = %s, 
                    prerequisites = %s, description = %s
                WHERE id = %s
            """
            
            self.session.execute(query, (
                course.course_name,
                course.credits,
                course.difficulty,
                course.prerequisites,
                course.description,
                course.id
            ))
            
            logger.info(f"Updated course: {course.id}")
            return course
        except Exception as e:
            logger.error(f"Error updating course: {str(e)}")
            raise
    
    def delete(self, course_id: UUID) -> bool:
        """Delete a course"""
        try:
            query = f"""
                DELETE FROM {self.keyspace}.courses 
                WHERE id = %s
            """
            self.session.execute(query, (course_id,))
            logger.info(f"Deleted course: {course_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting course: {str(e)}")
            return False
    
    def _map_row_to_course(self, row) -> Course:
        """Map Cassandra row to Course model"""
        return Course(
            id=row.id,
            course_code=row.course_code,
            course_name=row.course_name,
            credits=row.credits,
            difficulty=row.difficulty,
            prerequisites=list(row.prerequisites) if row.prerequisites else [],
            description=row.description or "",
            created_at=row.created_at
        )


# Singleton instance
course_repository = CourseRepository()
