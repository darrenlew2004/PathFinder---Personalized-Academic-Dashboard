"""
Subject Repository for Cassandra schema
Table: subjects (with 11 columns as per real schema)
"""

from typing import Optional, List
from uuid import UUID
import logging
from app.models import Subject, SubjectResponse
from app.services.cassandra_service import cassandra_service

logger = logging.getLogger(__name__)


class SubjectRepository:
    def __init__(self):
        self.session = cassandra_service.get_session()
        self.keyspace = "subjectplanning"
    
    def find_by_id(self, subject_id: int) -> Optional[Subject]:
        """Find subject by int ID"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.subjects 
                WHERE id = %s
            """
            result = self.session.execute(query, (subject_id,))
            row = result.one()
            
            if row:
                return self._map_row_to_subject(row)
            return None
        except Exception as e:
            logger.error(f"Error finding subject by id: {str(e)}")
            return None
    
    def find_by_subject_code(self, subjectcode: str) -> List[Subject]:
        """Find subjects by subject code"""
        try:
            query = f"""
                SELECT * FROM {self.keyspace}.subjects 
                WHERE subjectcode = %s 
                ALLOW FILTERING
            """
            result = self.session.execute(query, (subjectcode,))
            return [self._map_row_to_subject(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding subjects by code: {str(e)}")
            return []
    
    def find_by_programme_code(self, programmecode: str, limit: int = 50) -> List[Subject]:
        """Find subjects for a programme (with limit to avoid slow queries)"""
        try:
            # Add timeout and limit to prevent hanging
            query = f"""
                SELECT * FROM {self.keyspace}.subjects 
                WHERE programmecode = %s 
                LIMIT %s
                ALLOW FILTERING
            """
            result = self.session.execute(query, (programmecode, limit), timeout=5.0)
            return [self._map_row_to_subject(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding subjects by programme: {str(e)}")
            return []
    
    def find_all(self, limit: int = 100) -> List[Subject]:
        """Find all subjects (with limit)"""
        try:
            query = f"SELECT * FROM {self.keyspace}.subjects LIMIT %s"
            result = self.session.execute(query, (limit,))
            return [self._map_row_to_subject(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding all subjects: {str(e)}")
            return []
    
    def _map_row_to_subject(self, row) -> Subject:
        """Map Cassandra row to Subject model"""
        return Subject(
            id=row.id,
            programmecode=getattr(row, 'programmecode', None),
            subjectcode=getattr(row, 'subjectcode', None),
            subjectname=getattr(row, 'subjectname', None),
            examyear=getattr(row, 'examyear', None),
            exammonth=getattr(row, 'exammonth', None),
            status=getattr(row, 'status', None),
            attendancepercentage=getattr(row, 'attendancepercentage', None),
            courseworkpercentage=getattr(row, 'courseworkpercentage', None),
            grade=getattr(row, 'grade', None),
            overallpercentage=getattr(row, 'overallpercentage', None)
        )


# Singleton instance
subject_repository = SubjectRepository()
