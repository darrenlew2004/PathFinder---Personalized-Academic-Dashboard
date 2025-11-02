"""
Student stats routes that use the actual students/subjects tables
"""

from fastapi import APIRouter, HTTPException, status, Depends
import logging
from app.models.actual_models import StudentResponse, SubjectResponse, StudentWithSubjects
from app.repositories.student_repository_actual import student_repository_actual
from app.repositories.subject_repository_actual import subject_repository_actual
from app.services.jwt_service import jwt_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/students", tags=["Student Stats (Actual)"])


def get_current_user(authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    token = authorization.split(" ")[1]
    claims = jwt_service.validate_token(token)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    return claims


@router.get("/current", response_model=StudentResponse)
async def get_current_student(claims: dict = Depends(get_current_user)):
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
async def get_student_subjects(student_id: str):
    # Look up student
    try:
        from uuid import UUID
        sid = UUID(student_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student UUID")

    student = student_repository_actual.find_by_id(sid)
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
