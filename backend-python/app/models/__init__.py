from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"
    LECTURER = "LECTURER"


class CourseStatus(str, Enum):
    ENROLLED = "ENROLLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DROPPED = "DROPPED"


class StudentBase(BaseModel):
    student_id: str = Field(..., description="Student ID number")
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    gpa: float = Field(0.0, ge=0.0, le=4.0)
    semester: int = Field(1, ge=1)


class StudentCreate(StudentBase):
    password: str = Field(..., min_length=6)


class Student(StudentBase):
    id: UUID = Field(default_factory=uuid4)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class StudentResponse(StudentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    course_code: str = Field(..., max_length=50)
    course_name: str = Field(..., max_length=255)
    credits: int = Field(..., ge=1, le=6)
    difficulty: float = Field(..., ge=1.0, le=5.0, description="Course difficulty rating")
    prerequisites: List[str] = Field(default_factory=list)
    description: str = Field(default="")


class Course(CourseBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class EnrollmentBase(BaseModel):
    student_id: UUID
    course_id: UUID
    semester: int
    status: CourseStatus = CourseStatus.ENROLLED
    attendance_rate: float = Field(0.0, ge=0.0, le=1.0)


class Enrollment(EnrollmentBase):
    id: UUID = Field(default_factory=uuid4)
    grade: Optional[str] = None
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class RiskPredictionBase(BaseModel):
    student_id: UUID
    course_id: UUID
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    factors: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    predicted_grade: Optional[str] = None


class RiskPrediction(RiskPredictionBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class CourseProgress(BaseModel):
    course: Course
    enrollment: Enrollment
    risk_prediction: Optional[RiskPrediction] = None
    
    model_config = ConfigDict(from_attributes=True)


class StudentStats(BaseModel):
    student: StudentResponse
    current_courses: List[CourseProgress]
    completed_courses: int
    total_credits: int
    average_attendance: float
    risk_distribution: Dict[str, int]
    
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    student: StudentResponse


class ApiError(BaseModel):
    message: str
    code: Optional[str] = None
