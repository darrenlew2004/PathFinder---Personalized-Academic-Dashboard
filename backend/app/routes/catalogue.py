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
    logger.debug("[JWT] Starting token validation")
    from app.services.jwt_service import jwt_service

    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("[JWT] No authorization header provided")
        raise HTTPException(status_code=401, detail="No token provided")

    token = authorization.split(" ")[1]
    logger.debug(f"[JWT] Validating token: {token[:20]}...")
    claims = jwt_service.validate_token(token)
    logger.debug(f"[JWT] Token validated, claims: {claims}")

    if not claims:
        logger.warning("[JWT] Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    # jwt_service returns {'user_id': int|UUID|str, 'email': ...}
    user_id = claims["user_id"]
    logger.debug(f"[JWT] Returning user_id: {user_id}")
    return user_id


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


# Cache for electives to avoid rebuilding response
_ELECTIVES_CACHE = {}

@router.get("/variant/{variant_key}/electives")
async def get_variant_electives(variant_key: str):
    """Get elective groups and options for a variant (cached for performance)"""
    # Check cache first
    if variant_key in _ELECTIVES_CACHE:
        logger.info(f"Returning cached electives for {variant_key}")
        return _ELECTIVES_CACHE[variant_key]
    
    variants = get_variants()
    if variant_key not in variants:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    variant = variants[variant_key]
    
    # Build response
    response = {
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
    
    # Cache the response
    _ELECTIVES_CACHE[variant_key] = response
    logger.info(f"Cached electives for {variant_key}")
    
    return response


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


# Cache for student progress to avoid repeated Cassandra queries
_STUDENT_PROGRESS_CACHE = {}

@router.get("/student/progress")
async def get_student_progress(
    intake: str,
    entry_type: str,
    student_id: str = Depends(get_current_user)
):
    """Get authenticated student's progress (cached for performance)"""
    logger.info(f"[PROGRESS] Endpoint reached for intake={intake}, entry_type={entry_type}, student_id={student_id}")
    from app.repositories.student_repository import student_repository
    
    # Check cache first (5-minute TTL)
    cache_key = f"{student_id}:{intake}:{entry_type}"
    if cache_key in _STUDENT_PROGRESS_CACHE:
        cached_data, cached_time = _STUDENT_PROGRESS_CACHE[cache_key]
        import time
        if time.time() - cached_time < 300:  # 5 minutes
            logger.info(f"Returning cached progress for student {student_id}")
            return cached_data
    
    logger.info(f"Fetching progress for student {student_id}...")
    
    # Try CSV fallback first (fast), then Cassandra (slow)
    from app.services.csv_data_service import get_csv_service
    csv_service = get_csv_service()
    
    completed_codes = []
    data_source = "unknown"
    
    # Try CSV first (instant)
    if csv_service.is_available():
        try:
            logger.info(f"Attempting to fetch from CSV for student {student_id}")
            completed_codes = csv_service.get_completed_subject_codes(student_id)
            if completed_codes:
                data_source = "csv"
                logger.info(f"✓ CSV: Student {student_id} has {len(completed_codes)} completed subjects")
        except Exception as e:
            logger.warning(f"CSV fallback failed: {e}")
    
    # If CSV failed or not available, try Cassandra with timeout
    if not completed_codes:
        try:
            logger.info(f"Attempting to fetch from Cassandra for student {student_id}")
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
            
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(student_repository.find_by_id, student_id)
            
            try:
                student = future.result(timeout=5.0)  # 5 second timeout
            except FuturesTimeoutError:
                logger.error(f"⚠ Cassandra query timed out for student {student_id}")
                raise HTTPException(
                    status_code=504, 
                    detail="Database is slow. Please try again in a moment."
                )
            finally:
                executor.shutdown(wait=False)
            
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")

            completed_codes = student_repository.get_completed_subject_codes(student_id)
            data_source = "cassandra"
            logger.info(f"✓ Cassandra: Student {student_id} has {len(completed_codes)} completed subjects")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching from Cassandra: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching student data: {str(e)}")
    
    if not completed_codes:
        raise HTTPException(status_code=404, detail="Student not found in any data source")
    
    logger.info(f"Using data from: {data_source}")
    
    # Compute progress
    variants = get_variants()
    variant_key = f"{intake}-{entry_type}"
    
    if variant_key not in variants:
        raise HTTPException(status_code=404, detail=f"Variant {variant_key} not found")
    
    variant = variants[variant_key]
    progress = variant.compute_progress(set(completed_codes))
    
    response = ProgressResponse(
        completed_credits=progress.completed_credits,
        total_credits=progress.total_credits,
        outstanding_credits=progress.outstanding_credits,
        core_remaining=progress.core_remaining,
        discipline_elective_placeholders_remaining=progress.discipline_elective_placeholders_remaining,
        free_elective_placeholders_remaining=progress.free_elective_placeholders_remaining,
        either_pairs_remaining=progress.either_pairs_remaining,
        percent_complete=progress.percent_complete
    )
    
    # Cache the response
    import time
    _STUDENT_PROGRESS_CACHE[cache_key] = (response, time.time())
    if len(_STUDENT_PROGRESS_CACHE) > 100:
        # Clear oldest 50% of cache
        sorted_items = sorted(_STUDENT_PROGRESS_CACHE.items(), key=lambda x: x[1][1])
        _STUDENT_PROGRESS_CACHE.clear()
        _STUDENT_PROGRESS_CACHE.update(dict(sorted_items[50:]))
    
    logger.info(f"Progress computed and cached for student {student_id}")
    return response


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
