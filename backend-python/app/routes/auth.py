from fastapi import APIRouter, HTTPException, status
from typing import Dict
import logging
from app.models import LoginRequest, LoginResponse, StudentCreate, StudentResponse
from app.repositories.student_repository import student_repository
from app.services.jwt_service import jwt_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate a user and return JWT token"""
    try:
        # Find student by email
        student = student_repository.find_by_email(request.email)
        
        if not student:
            logger.warning(f"User not found: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not student_repository.verify_password(student, request.password):
            logger.warning(f"Invalid password for: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate JWT token
        token = jwt_service.generate_token(student.id, student.email)
        
        logger.info(f"User logged in: {student.email}")
        
        return LoginResponse(
            token=token,
            student=StudentResponse(
                id=student.id,
                student_id=student.student_id,
                name=student.name,
                email=student.email,
                gpa=student.gpa,
                semester=student.semester,
                created_at=student.created_at,
                updated_at=student.updated_at
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.post("/logout")
async def logout():
    """Logout user (JWT handled client-side)"""
    logger.info("User logged out")
    return {"message": "Logged out successfully"}


@router.post("/register", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def register(student_data: StudentCreate):
    """Register a new student"""
    try:
        # Check if email already exists
        existing_student = student_repository.find_by_email(student_data.email)
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if student ID already exists
        existing_student_id = student_repository.find_by_student_id(student_data.student_id)
        if existing_student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID already registered"
            )
        
        # Create new student
        student = student_repository.create(student_data)
        
        logger.info(f"New student registered: {student.email}")
        
        return StudentResponse(
            id=student.id,
            student_id=student.student_id,
            name=student.name,
            email=student.email,
            gpa=student.gpa,
            semester=student.semester,
            created_at=student.created_at,
            updated_at=student.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


@router.get("/verify")
async def verify_token(authorization: str = None):
    """Verify JWT token from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    token = authorization.split(" ")[1]
    claims = jwt_service.validate_token(token)
    
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {
        "valid": True,
        "userId": str(claims["user_id"]),
        "email": claims["email"]
    }
