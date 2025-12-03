"""
Student stats routes using students/subjects tables
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional
import logging
from app.models import StudentResponse, SubjectResponse, StudentWithSubjects

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("/list", response_model=list[StudentResponse])
async def list_students(limit: int = 10):
    """List students (for testing - shows IC numbers you can use to login)
    Returns 503 if Cassandra is unavailable.
    """
    try:
        from app.repositories.student_repository import student_repository
        students = student_repository.find_all(limit=limit)
    except Exception as e:
        logger.error(f"Cassandra error listing students: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database unavailable")

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
            cohort=s.cohort,
            gender=s.gender,
            race=s.race,
            country=s.country,
            yearonecgpa=s.yearonecgpa
        ) for s in students
    ]


def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract and validate JWT token from Authorization header"""
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
    from app.repositories.student_repository import student_repository
    
    student_id = claims["user_id"]
    student = student_repository.find_by_id(student_id)
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
        cohort=student.cohort,
        gender=student.gender,
        race=student.race,
        country=student.country,
        yearonecgpa=student.yearonecgpa
    )


@router.get("/{student_id}/subjects", response_model=StudentWithSubjects)
async def get_student_subjects(student_id: int, limit: int = 50):
    """Get student and their subjects by student ID (int).
    Prefer reading the student's own `subjects/subject` column from the students table,
    and fall back to programme-level subjects if unavailable.
    """
    from app.repositories.student_repository import student_repository
    from app.repositories.subject_repository import subject_repository
    import logging
    
    logger = logging.getLogger(__name__)
    
    student = student_repository.find_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # First, attempt to read from student's subjects column
    subject_entries = []
    try:
        subject_entries = student_repository.get_subject_entries(student_id)
    except Exception as e:
        logger.error(f"Error reading student's subjects column: {str(e)}")
        subject_entries = []

    subject_responses = []
    if subject_entries:
        # Map normalized dicts to SubjectResponse with synthetic IDs
        for idx, e in enumerate(subject_entries, start=1):
            try:
                subject_responses.append(SubjectResponse(
                    id=idx,
                    subjectcode=e.get('subjectcode'),
                    subjectname=e.get('subjectname'),
                    programmecode=student.programmecode,
                    grade=e.get('grade'),
                    overallpercentage=e.get('overallpercentage'),
                    attendancepercentage=e.get('attendancepercentage'),
                    courseworkpercentage=e.get('courseworkpercentage'),
                    status=e.get('status'),
                    examyear=e.get('examyear'),
                    exammonth=e.get('exammonth')
                ))
            except Exception as ex:
                logger.warning(f"Error mapping student subject entry: {str(ex)}")
                continue
    else:
        # Fallback: programme-level subjects
        subjects = []
        if student.programmecode:
            try:
                logger.info(f"Fetching subjects for programme: {student.programmecode}, limit: {limit}")
                subjects = subject_repository.find_by_programme_code(student.programmecode, limit=limit)
                logger.info(f"Found {len(subjects)} subjects")
            except Exception as e:
                logger.error(f"Error fetching subjects: {str(e)}")
                subjects = []

        for s in subjects:
            try:
                subject_responses.append(SubjectResponse(
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
                ))
            except Exception as e:
                logger.warning(f"Error mapping subject {getattr(s, 'id', 'unknown')}: {str(e)}")
                continue

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
