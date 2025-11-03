"""
Models matching the ACTUAL Cassandra database schema
Tables: students, subjects
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from uuid import UUID, uuid4


# ==================== STUDENT MODELS ====================

class Student(BaseModel):
    """Student model matching actual Cassandra table structure"""
    id: int  # INT in Cassandra, not UUID!
    program: Optional[str] = None
    awardclassification: Optional[str] = None
    broadsheetyear: Optional[int] = None
    cavg: Optional[float] = None
    cohort: Optional[str] = None
    country: Optional[str] = None
    finanicalaid: Optional[str] = None  # Note: typo in DB
    gender: Optional[str] = None
    graduated: Optional[bool] = None
    ic: Optional[str] = None  # IC number - unique identifier
    name: Optional[str] = None
    overallcavg: Optional[float] = None
    overallcgpa: Optional[float] = None
    programmecode: Optional[str] = None
    qualifications: Optional[Any] = None  # SortedSet - complex type
    race: Optional[str] = None
    sem: Optional[int] = None
    sponsorname: Optional[str] = None
    status: Optional[str] = None
    subjects: Optional[Any] = None  # List of maps - complex type
    year: Optional[int] = None
    yearonaverage: Optional[float] = None
    yearonecgpa: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class StudentCreate(BaseModel):
    """For creating a new student"""
    ic: str  # Required: IC number
    name: str  # Required: Student name
    programmecode: Optional[str] = None
    year: Optional[int] = None
    sem: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None


class StudentResponse(BaseModel):
    """API response model for student"""
    id: int  # INT, not UUID
    ic: Optional[str] = None
    name: Optional[str] = None
    programmecode: Optional[str] = None
    program: Optional[str] = None
    overallcgpa: Optional[float] = None
    overallcavg: Optional[float] = None
    year: Optional[int] = None
    sem: Optional[int] = None
    status: Optional[str] = None
    graduated: Optional[bool] = None
    cohort: Optional[str] = None


# ==================== SUBJECT MODELS ====================

class Subject(BaseModel):
    """Subject model matching actual Cassandra table structure"""
    id: int  # INT in Cassandra
    programmecode: Optional[str] = None
    subjectcode: Optional[str] = None
    subjectname: Optional[str] = None
    examyear: Optional[int] = None
    exammonth: Optional[int] = None
    status: Optional[str] = None
    attendancepercentage: Optional[float] = None
    courseworkpercentage: Optional[float] = None
    grade: Optional[str] = None
    overallpercentage: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class SubjectResponse(BaseModel):
    """API response model for subject"""
    id: int
    subjectcode: Optional[str] = None
    subjectname: Optional[str] = None
    programmecode: Optional[str] = None
    grade: Optional[str] = None
    overallpercentage: Optional[float] = None
    attendancepercentage: Optional[float] = None
    courseworkpercentage: Optional[float] = None
    status: Optional[str] = None
    examyear: Optional[int] = None
    exammonth: Optional[int] = None


# ==================== COMBINED MODELS ====================

class StudentWithSubjects(BaseModel):
    """Student with their subjects"""
    student: StudentResponse
    subjects: List[SubjectResponse] = []
    total_subjects: int = 0
    average_grade: Optional[float] = None
    average_attendance: Optional[float] = None


# ==================== AUTH MODELS ====================

class LoginRequest(BaseModel):
    """Login with student ID (int)"""
    student_id: int


class LoginResponse(BaseModel):
    """Login response with JWT token"""
    token: str
    student: StudentResponse


# ==================== ERROR MODEL ====================

class ApiError(BaseModel):
    """Standard API error response"""
    error: str
    detail: Optional[str] = None
