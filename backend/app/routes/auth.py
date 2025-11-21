"""
Auth routes for student authentication using student ID
"""

from fastapi import APIRouter, HTTPException, status
import logging
from app.models import LoginRequest, LoginResponse, StudentResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate using student ID (int primary key)
    Simplified - no password in current schema
    """
    # Lazy import to avoid cassandra driver init issues
    from app.repositories.student_repository import student_repository
    from app.services.jwt_service import jwt_service
    
    try:
        # Find student by ID
        student = student_repository.find_by_id(request.student_id)
        
        if not student:
            logger.warning(f"Student not found: {request.student_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid student ID"
            )
        
        # Generate JWT token (use str(id) as identifier)
        token = jwt_service.generate_token(student.id, str(student.id))
        
        logger.info(f"Student logged in: {student.id} - {student.name}")
        
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


@router.post("/refresh")
async def refresh_token(request: dict):
    """
    Refresh JWT token
    Note: In production, you'd want to use refresh tokens with different expiration
    """
    from app.services.jwt_service import jwt_service
    
    token = request.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token required"
        )
    
    # Validate the old token
    claims = jwt_service.validate_token(token)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Generate new token with same claims
    new_token = jwt_service.generate_token(claims["user_id"], claims.get("email", ""))
    
    return {"token": new_token}


@router.get("/verify")
async def verify_token(authorization: str = None):
    """Verify JWT token from Authorization header"""
    from app.services.jwt_service import jwt_service
    
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
