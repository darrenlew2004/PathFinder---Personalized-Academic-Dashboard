"""
Student stats routes that use the actual students/subjects tables
"""

from fastapi import APIRouter, HTTPException, status, Depends
import logging
from app.models.actual_models import StudentResponse, SubjectResponse, StudentWithSubjects

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api-actual/students", tags=["Student Stats (Actual)"])


@router.get("/list", response_model=list[StudentResponse])
async def list_students(limit: int = 10):
    """List students (for testing - shows IC numbers you can use to login)"""
    from app.repositories.student_repository_actual import student_repository_actual
    
    students = student_repository_actual.find_all(limit=limit)
    return [
        StudentResponse(
            id=s.id,
            ic=s.ic,
            name=s.name,
            programmecode=s.programmecode,
            program=s.program,
            overallcgpa=s.overallcgpa,
            overallcavg=s.overallcavg,
            year=s.year,
            sem=s.sem,
            status=s.status,
            graduated=s.graduated,
            cohort=s.cohort
        ) for s in students
    ]


def get_current_user(authorization: str = None):
    from app.services.jwt_service import jwt_service
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    token = authorization.split(" ")[1]
    claims = jwt_service.validate_token(token)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    return claims


@router.get("/current", response_model=StudentResponse)
async def get_current_student(claims: dict = Depends(get_current_user)):
    from app.repositories.student_repository_actual import student_repository_actual
    
    student_id = claims["user_id"]
    student = student_repository_actual.find_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse(
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


@router.get("/{student_id}/subjects", response_model=StudentWithSubjects)
async def get_student_subjects(student_id: int):
    """Get student and their subjects by student ID (int)"""
    from app.repositories.student_repository_actual import student_repository_actual
    from app.repositories.subject_repository_actual import subject_repository_actual
    
    student = student_repository_actual.find_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get subjects by programme code (best-effort assumption)
    subjects = []
    if student.programmecode:
        subjects = subject_repository_actual.find_by_programme_code(student.programmecode)

    # Build response
    subject_responses = [
        SubjectResponse(
            id=s.id,
            subjectcode=s.subjectcode,
            subjectname=s.subjectname,
            programmecode=s.programmecode,
            grade=s.grade,
            overallpercentage=s.overallpercentage,
            attendancepercentage=s.attendancepercentage,
            courseworkpercentage=s.courseworkpercentage,
            status=s.status,
            examyear=s.examyear,
            exammonth=s.exammonth
        ) for s in subjects
    ]

    avg_att = None
    avg_pct = None
    if subject_responses:
        att_values = [s.attendancepercentage for s in subject_responses if s.attendancepercentage is not None]
        pct_values = [s.overallpercentage for s in subject_responses if s.overallpercentage is not None]
        avg_att = sum(att_values)/len(att_values) if att_values else None
        avg_pct = sum(pct_values)/len(pct_values) if pct_values else None

    return StudentWithSubjects(
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
        ),
        subjects=subject_responses,
        total_subjects=len(subject_responses),
        average_attendance=avg_att,
        average_percentage=avg_pct
    )
