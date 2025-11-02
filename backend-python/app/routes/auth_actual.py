"""
Auth routes adapted for actual schema (no password/email)
Using IC number for identification
"""

from fastapi import APIRouter, HTTPException, status
import logging
from app.models.actual_models import LoginRequest, LoginResponse, StudentResponse
from app.repositories.student_repository_actual import student_repository_actual
from app.services.jwt_service import jwt_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate using IC number (simplified - no password in current schema)
    In production, you'd need to add password column to students table
    """
    try:
        # Find student by IC
        student = student_repository_actual.find_by_ic(request.ic)
        
        if not student:
            logger.warning(f"Student not found: {request.ic}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid IC number"
            )
        
        # Generate JWT token
        token = jwt_service.generate_token(student.id, student.ic or "")
        
        logger.info(f"Student logged in: {student.ic}")
        
        return LoginResponse(
            token=token,
            student=StudentResponse(
                id=student.id,
                ic=student.ic,
                name=student.name,
                programmecode=student.programmecode,
                program=student.program,
                overallcgpa=student.overallcgpa,
                overallcavg=student.overallcavg,
                year=student.year,
                sem=student.sem,
                status=student.status,
                graduated=student.graduated,
                cohort=student.cohort
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
        "ic": claims.get("email", "")  # "email" field in JWT actually contains IC
    }
