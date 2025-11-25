"""
Programme Catalogue API routes for progress tracking, risk prediction, and recommendations
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

from app.catalog.bcs_programs import load_bcs_variants
from app.catalog.program_catalog_models import RiskEngine, ProgressReport, CourseRisk, WhatIfResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/catalogue", tags=["Programme Catalogue"])

# Cache variants at module level
_VARIANTS_CACHE = None

def get_variants():
    global _VARIANTS_CACHE
    if _VARIANTS_CACHE is None:
        _VARIANTS_CACHE = load_bcs_variants()
    return _VARIANTS_CACHE


# Pydantic models for request/response
class ProgressRequest(BaseModel):
    intake: str  # e.g. "202301"
    entry_type: str  # "normal" | "direct" | "precalc"
    completed_codes: List[str]


class WhatIfRequest(BaseModel):
    intake: str
    entry_type: str
    planned_codes: List[str]
    completed_codes: List[str]
    cgpa: float
    attendance: float
    gpa_trend: float = 0.0


class CourseInfo(BaseModel):
    subject_code: str
    subject_name: str
    credit: int
    semester_offering: Optional[int]
    category: str
    elective_group: Optional[str]
    prerequisites: List[str]
    is_placeholder: bool


class ElectiveGroupInfo(BaseModel):
    group_code: str
    year_level: Optional[int]
    options: List[CourseInfo]


class ProgressResponse(BaseModel):
    completed_credits: int
    total_credits: int
    outstanding_credits: int
    core_remaining: List[str]
    discipline_elective_placeholders_remaining: List[str]
    free_elective_placeholders_remaining: List[str]
    either_pairs_remaining: List[List[str]]
    percent_complete: float


class CourseRiskResponse(BaseModel):
    subject_code: str
    subject_name: str
    predicted_risk: str
    numeric_score: float
    factors: Dict[str, float]


class WhatIfResponse(BaseModel):
    selected_subject_codes: List[str]
    total_credits: int
    aggregated_risk_score: float
    risk_band: str
    per_course: List[CourseRiskResponse]


def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract and validate JWT token from Authorization header and return numeric user_id."""
    from app.services.jwt_service import jwt_service

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = authorization.split(" ")[1]
    claims = jwt_service.validate_token(token)

    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")

    # jwt_service returns {'user_id': int|UUID|str, 'email': ...}
    return claims["user_id"]


@router.get("/variants")
async def list_variants():
    """List all available programme variants"""
    variants = get_variants()
    return {
        "variants": list(variants.keys()),
        "count": len(variants)
    }


@router.get("/variant/{variant_key}/courses")
async def get_variant_courses(variant_key: str):
    """Get all courses in a programme variant"""
    variants = get_variants()
    if variant_key not in variants:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    variant = variants[variant_key]
    courses = variant.list_all_courses()
    
    return {
        "variant": variant_key,
        "total_courses": len(courses),
        "courses": [
            CourseInfo(
                subject_code=c.subject_code,
                subject_name=c.subject_name,
                credit=c.credit,
                semester_offering=c.semester_offering,
                category=c.category,
                elective_group=c.elective_group,
                prerequisites=c.prerequisites,
                is_placeholder=c.is_placeholder
            )
            for c in courses
        ]
    }


@router.get("/variant/{variant_key}/electives")
async def get_variant_electives(variant_key: str):
    """Get elective groups and options for a variant"""
    variants = get_variants()
    if variant_key not in variants:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    variant = variants[variant_key]
    
    return {
        "variant": variant_key,
        "elective_groups": {
            code: ElectiveGroupInfo(
                group_code=group.group_code,
                year_level=group.year_level,
                options=[
                    CourseInfo(
                        subject_code=c.subject_code,
                        subject_name=c.subject_name,
                        credit=c.credit,
                        semester_offering=c.semester_offering,
                        category=c.category,
                        elective_group=c.elective_group,
                        prerequisites=c.prerequisites,
                        is_placeholder=c.is_placeholder
                    )
                    for c in group.options
                ]
            )
            for code, group in variant.elective_groups.items()
        }
    }


@router.post("/progress", response_model=ProgressResponse)
async def compute_progress(request: ProgressRequest):
    """Compute student progress for a given variant"""
    variants = get_variants()
    variant_key = f"{request.intake}-{request.entry_type}"
    
    if variant_key not in variants:
        raise HTTPException(status_code=404, detail=f"Variant {variant_key} not found")
    
    variant = variants[variant_key]
    completed_set = set(request.completed_codes)
    progress = variant.compute_progress(completed_set)
    
    return ProgressResponse(
        completed_credits=progress.completed_credits,
        total_credits=progress.total_credits,
        outstanding_credits=progress.outstanding_credits,
        core_remaining=progress.core_remaining,
        discipline_elective_placeholders_remaining=progress.discipline_elective_placeholders_remaining,
        free_elective_placeholders_remaining=progress.free_elective_placeholders_remaining,
        either_pairs_remaining=progress.either_pairs_remaining,
        percent_complete=progress.percent_complete
    )


@router.post("/what-if", response_model=WhatIfResponse)
async def what_if_analysis(request: WhatIfRequest):
    """Perform what-if risk analysis for planned courses"""
    variants = get_variants()
    variant_key = f"{request.intake}-{request.entry_type}"
    
    if variant_key not in variants:
        raise HTTPException(status_code=404, detail=f"Variant {variant_key} not found")
    
    variant = variants[variant_key]
    engine = RiskEngine(variant)
    
    student_metrics = {
        'cgpa': request.cgpa,
        'attendance': request.attendance,
        'gpa_trend': request.gpa_trend,
        'planned_credits': 0  # computed in what_if
    }
    
    completed_set = set(request.completed_codes)
    result = engine.what_if(request.planned_codes, student_metrics, completed_set)
    
    return WhatIfResponse(
        selected_subject_codes=result.selected_subject_codes,
        total_credits=result.total_credits,
        aggregated_risk_score=result.aggregated_risk_score,
        risk_band=result.risk_band,
        per_course=[
            CourseRiskResponse(
                subject_code=cr.subject_code,
                subject_name=cr.subject_name,
                predicted_risk=cr.predicted_risk,
                numeric_score=cr.numeric_score,
                factors=cr.factors
            )
            for cr in result.per_course
        ]
    )


@router.get("/student/progress")
async def get_student_progress(
    intake: str,
    entry_type: str,
    student_id: str = Depends(get_current_user)
):
    """Get authenticated student's progress"""
    from app.repositories.student_repository import student_repository
    
    # Fetch student and derive completed subject codes from student's stored column
    student = student_repository.find_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    completed_codes = student_repository.get_completed_subject_codes(student_id)
    
    # Compute progress
    variants = get_variants()
    variant_key = f"{intake}-{entry_type}"
    
    if variant_key not in variants:
        raise HTTPException(status_code=404, detail=f"Variant {variant_key} not found")
    
    variant = variants[variant_key]
    progress = variant.compute_progress(set(completed_codes))
    
    return ProgressResponse(
        completed_credits=progress.completed_credits,
        total_credits=progress.total_credits,
        outstanding_credits=progress.outstanding_credits,
        core_remaining=progress.core_remaining,
        discipline_elective_placeholders_remaining=progress.discipline_elective_placeholders_remaining,
        free_elective_placeholders_remaining=progress.free_elective_placeholders_remaining,
        either_pairs_remaining=progress.either_pairs_remaining,
        percent_complete=progress.percent_complete
    )


@router.get("/student/recommendations")
async def get_recommendations(
    intake: str,
    entry_type: str,
    student_id: str = Depends(get_current_user)
):
    """Get course recommendations for authenticated student"""
    from app.repositories.student_repository import student_repository
    
    student = student_repository.find_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    completed_codes = set(student_repository.get_completed_subject_codes(student_id))
    
    variants = get_variants()
    variant_key = f"{intake}-{entry_type}"
    
    if variant_key not in variants:
        raise HTTPException(status_code=404, detail=f"Variant {variant_key} not found")
    
    variant = variants[variant_key]
    future_courses = variant.future_courses_for_student(completed_codes)
    
    # Simple recommendation: filter by prerequisite satisfaction
    recommended = []
    for course in future_courses[:20]:  # limit to 20
        prereqs = variant.prerequisite_graph.get(course.subject_code, [])
        if all(p in completed_codes for p in prereqs):
            recommended.append(
                CourseInfo(
                    subject_code=course.subject_code,
                    subject_name=course.subject_name,
                    credit=course.credit,
                    semester_offering=course.semester_offering,
                    category=course.category,
                    elective_group=course.elective_group,
                    prerequisites=prereqs,
                    is_placeholder=course.is_placeholder
                )
            )
    
    return {
        "student_id": student_id,
        "variant": variant_key,
        "recommended_courses": recommended,
        "count": len(recommended)
    }
