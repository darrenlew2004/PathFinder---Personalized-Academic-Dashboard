from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional, Dict, List
from uuid import UUID
import logging
from app.models import StudentStats, CourseProgress, StudentResponse, RiskLevel
from app.repositories.student_repository import student_repository
from app.repositories.course_repository import course_repository
from app.repositories.enrollment_repository import enrollment_repository
from app.services.jwt_service import jwt_service
from app.services.risk_prediction_service import risk_prediction_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/students", tags=["Student Stats"])


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    """Dependency to get current authenticated user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = authorization.split(" ")[1]
    claims = jwt_service.validate_token(token)
    
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return claims


@router.get("/current", response_model=StudentResponse)
async def get_current_student(current_user: Dict = Depends(get_current_user)):
    """Get current authenticated student's information"""
    try:
        student = student_repository.find_by_id(current_user["user_id"])
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
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
        logger.error(f"Error getting current student: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching student data"
        )


@router.get("/{student_id}/stats", response_model=StudentStats)
async def get_student_stats(student_id: str, current_user: Dict = Depends(get_current_user)):
    """Get comprehensive statistics for a student"""
    try:
        # Find student
        student = student_repository.find_by_id(UUID(student_id))
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Get all enrollments
        enrollments = enrollment_repository.find_by_student_id(student.id)
        
        # Get current enrollments
        current_enrollments = enrollment_repository.find_current_enrollments(student.id)
        
        # Get completed enrollments
        completed_enrollments = enrollment_repository.find_completed_enrollments(student.id)
        
        # Build course progress for current courses
        current_courses: List[CourseProgress] = []
        for enrollment in current_enrollments:
            course = course_repository.find_by_id(enrollment.course_id)
            if course:
                # Get risk prediction
                risk_pred = risk_prediction_service.predict_risk(student, course, enrollments)
                
                current_courses.append(CourseProgress(
                    course=course,
                    enrollment=enrollment,
                    risk_prediction=risk_pred
                ))
        
        # Calculate total credits
        total_credits = sum(
            course_repository.find_by_id(e.course_id).credits 
            for e in completed_enrollments 
            if course_repository.find_by_id(e.course_id)
        )
        
        # Calculate average attendance
        avg_attendance = (
            sum(e.attendance_rate for e in enrollments) / len(enrollments)
            if enrollments else 0.0
        )
        
        # Calculate risk distribution
        risk_distribution = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0
        }
        for cp in current_courses:
            if cp.risk_prediction:
                risk_distribution[cp.risk_prediction.risk_level.value] += 1
        
        return StudentStats(
            student=StudentResponse(
                id=student.id,
                student_id=student.student_id,
                name=student.name,
                email=student.email,
                gpa=student.gpa,
                semester=student.semester,
                created_at=student.created_at,
                updated_at=student.updated_at
            ),
            current_courses=current_courses,
            completed_courses=len(completed_enrollments),
            total_credits=total_credits,
            average_attendance=avg_attendance,
            risk_distribution=risk_distribution
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching student statistics"
        )


@router.get("/{student_id}/progress", response_model=List[CourseProgress])
async def get_course_progress(student_id: str, current_user: Dict = Depends(get_current_user)):
    """Get course progress for a student"""
    try:
        student = student_repository.find_by_id(UUID(student_id))
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Get current enrollments
        current_enrollments = enrollment_repository.find_current_enrollments(student.id)
        all_enrollments = enrollment_repository.find_by_student_id(student.id)
        
        course_progress: List[CourseProgress] = []
        for enrollment in current_enrollments:
            course = course_repository.find_by_id(enrollment.course_id)
            if course:
                # Get risk prediction
                risk_pred = risk_prediction_service.predict_risk(student, course, all_enrollments)
                
                course_progress.append(CourseProgress(
                    course=course,
                    enrollment=enrollment,
                    risk_prediction=risk_pred
                ))
        
        return course_progress
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching course progress"
        )


@router.get("/{student_id}/risks", response_model=List[Dict])
async def get_risk_predictions(student_id: str, current_user: Dict = Depends(get_current_user)):
    """Get risk predictions for a student's current courses"""
    try:
        student = student_repository.find_by_id(UUID(student_id))
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Get current enrollments
        current_enrollments = enrollment_repository.find_current_enrollments(student.id)
        all_enrollments = enrollment_repository.find_by_student_id(student.id)
        
        # Get courses
        current_courses = []
        for enrollment in current_enrollments:
            course = course_repository.find_by_id(enrollment.course_id)
            if course:
                current_courses.append(course)
        
        # Get risk predictions
        predictions = risk_prediction_service.predict_risks_for_student(
            student, current_courses, all_enrollments
        )
        
        # Format response
        return [
            {
                "id": str(pred.id),
                "student_id": str(pred.student_id),
                "course_id": str(pred.course_id),
                "risk_level": pred.risk_level.value,
                "confidence": pred.confidence,
                "factors": pred.factors,
                "recommendations": pred.recommendations,
                "predicted_grade": pred.predicted_grade,
                "created_at": pred.created_at.isoformat()
            }
            for pred in predictions
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk predictions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching risk predictions"
        )
