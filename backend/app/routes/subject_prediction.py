"""
Subject Prediction API Routes

Endpoints for predicting student success in subjects based on
prerequisite performance and historical data.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ..services.subject_prediction_service import (
    get_prediction_service,
    SubjectPrediction,
    StudentPredictionReport,
    PrerequisitePerformance
)
from ..routes.student_stats import get_current_user

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


# Pydantic models for API responses
class PrerequisitePerformanceResponse(BaseModel):
    subject_code: str
    subject_name: str
    grade: str
    grade_points: float
    weight: float
    impact_score: float


class SubjectPredictionResponse(BaseModel):
    subject_code: str
    subject_name: str
    risk_level: str
    predicted_success_probability: float
    weighted_prereq_gpa: float
    prereq_performance: List[PrerequisitePerformanceResponse]
    missing_prereqs: List[str]
    recommendation: str
    cohort_pass_rate: Optional[float] = None
    cohort_avg_score: Optional[float] = None
    # ML hybrid fields
    ml_probability: Optional[float] = None
    ml_confidence: Optional[float] = None
    ml_top_factors: Optional[List[tuple]] = None
    prediction_method: str = 'rule-based'


class StudentPredictionReportResponse(BaseModel):
    student_id: int
    current_gpa: float
    predictions: List[SubjectPredictionResponse]
    high_risk_subjects: List[str]
    recommended_order: List[str]


class PredictRequest(BaseModel):
    subject_codes: List[str]


class PrerequisiteChainResponse(BaseModel):
    subject_code: str
    subject_name: str
    direct_prerequisites: List[Dict[str, Any]]
    full_chain: List[Dict[str, Any]]


class CohortStatsResponse(BaseModel):
    subject_code: str
    subject_name: str
    pass_rate: Optional[float]
    avg_score: Optional[float]
    avg_gpa: Optional[float]
    total_students: int


def _convert_prediction(pred: SubjectPrediction) -> SubjectPredictionResponse:
    """Convert dataclass to Pydantic model"""
    return SubjectPredictionResponse(
        subject_code=pred.subject_code,
        subject_name=pred.subject_name,
        risk_level=pred.risk_level,
        predicted_success_probability=pred.predicted_success_probability,
        weighted_prereq_gpa=pred.weighted_prereq_gpa,
        prereq_performance=[
            PrerequisitePerformanceResponse(
                subject_code=p.subject_code,
                subject_name=p.subject_name,
                grade=p.grade,
                grade_points=p.grade_points,
                weight=p.weight,
                impact_score=p.impact_score
            ) for p in pred.prereq_performance
        ],
        missing_prereqs=pred.missing_prereqs,
        recommendation=pred.recommendation,
        cohort_pass_rate=pred.cohort_pass_rate,
        cohort_avg_score=pred.cohort_avg_score,
        ml_probability=pred.ml_probability,
        ml_confidence=pred.ml_confidence,
        ml_top_factors=pred.ml_top_factors,
        prediction_method=pred.prediction_method
    )


@router.get("/students/{student_id}/subject/{subject_code}", response_model=SubjectPredictionResponse)
async def predict_single_subject(student_id: int, subject_code: str):
    """
    Predict success probability for a single subject based on student's
    performance in prerequisite subjects.
    """
    service = get_prediction_service()
    
    if service.df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    
    # Check if student exists
    if student_id not in service.df['student_id'].values:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    prediction = service.predict_subject_success(student_id, subject_code)
    return _convert_prediction(prediction)


@router.post("/students/{student_id}/subjects", response_model=StudentPredictionReportResponse)
async def predict_multiple_subjects(student_id: int, request: PredictRequest):
    """
    Predict success probability for multiple subjects.
    Returns predictions ordered by risk level with recommendations.
    """
    service = get_prediction_service()
    
    if service.df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    
    if student_id not in service.df['student_id'].values:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    if not request.subject_codes:
        raise HTTPException(status_code=400, detail="No subject codes provided")
    
    report = service.predict_multiple_subjects(student_id, request.subject_codes)
    
    return StudentPredictionReportResponse(
        student_id=report.student_id,
        current_gpa=report.current_gpa,
        predictions=[_convert_prediction(p) for p in report.predictions],
        high_risk_subjects=report.high_risk_subjects,
        recommended_order=report.recommended_order
    )


@router.get("/current/subject/{subject_code}", response_model=SubjectPredictionResponse)
async def predict_current_student_subject(
    subject_code: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Predict success probability for a subject for the currently logged-in student.
    """
    student_id = current_user.get('user_id')
    if not student_id:
        raise HTTPException(status_code=401, detail="Student ID not found in token")
    
    service = get_prediction_service()
    
    if service.df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    
    prediction = service.predict_subject_success(int(student_id), subject_code)
    return _convert_prediction(prediction)


@router.post("/current/subjects", response_model=StudentPredictionReportResponse)
async def predict_current_student_subjects(
    request: PredictRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Predict success for multiple subjects for the currently logged-in student.
    """
    student_id = current_user.get('user_id')
    if not student_id:
        raise HTTPException(status_code=401, detail="Student ID not found in token")
    
    service = get_prediction_service()
    
    if service.df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    
    if not request.subject_codes:
        raise HTTPException(status_code=400, detail="No subject codes provided")
    
    report = service.predict_multiple_subjects(int(student_id), request.subject_codes)
    
    return StudentPredictionReportResponse(
        student_id=report.student_id,
        current_gpa=report.current_gpa,
        predictions=[_convert_prediction(p) for p in report.predictions],
        high_risk_subjects=report.high_risk_subjects,
        recommended_order=report.recommended_order
    )


@router.get("/prerequisites/{subject_code}", response_model=PrerequisiteChainResponse)
async def get_prerequisite_chain(subject_code: str):
    """
    Get the prerequisite chain for a subject.
    Shows both direct prerequisites and the full dependency tree.
    """
    service = get_prediction_service()
    chain = service.get_prerequisite_chain(subject_code)
    
    return PrerequisiteChainResponse(
        subject_code=chain['subject_code'],
        subject_name=chain['subject_name'],
        direct_prerequisites=chain['direct_prerequisites'],
        full_chain=chain['full_chain']
    )


@router.get("/cohort-stats/{subject_code}", response_model=CohortStatsResponse)
async def get_cohort_stats(subject_code: str):
    """
    Get historical cohort statistics for a subject.
    Includes pass rate, average score, and number of students.
    """
    service = get_prediction_service()
    stats = service.cohort_stats.get(subject_code)
    
    if not stats:
        raise HTTPException(status_code=404, detail=f"No data for subject {subject_code}")
    
    return CohortStatsResponse(
        subject_code=subject_code,
        subject_name=stats.get('subject_name', subject_code),
        pass_rate=stats.get('pass_rate'),
        avg_score=stats.get('avg_score'),
        avg_gpa=stats.get('avg_gpa'),
        total_students=stats.get('total_students', 0)
    )


@router.get("/cohort-stats", response_model=List[CohortStatsResponse])
async def get_all_cohort_stats():
    """
    Get historical cohort statistics for all subjects.
    """
    service = get_prediction_service()
    
    return [
        CohortStatsResponse(
            subject_code=code,
            subject_name=stats.get('subject_name', code),
            pass_rate=stats.get('pass_rate'),
            avg_score=stats.get('avg_score'),
            avg_gpa=stats.get('avg_gpa'),
            total_students=stats.get('total_students', 0)
        )
        for code, stats in service.cohort_stats.items()
    ]
