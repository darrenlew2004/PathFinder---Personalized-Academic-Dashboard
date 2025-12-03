from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional

from app.models import StudentProfile
from app.services.student_analytics_service import get_student_profile
from app.routes.student_stats import get_current_user

router = APIRouter(prefix="/api/students", tags=["Students Analytics"])


@router.get("/{student_id}/analytics", response_model=StudentProfile)
async def student_analytics(student_id: int):
    profile = get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student or data not found")
    return profile


@router.get("/current/analytics", response_model=StudentProfile)
async def current_student_analytics(claims: dict = Depends(get_current_user)):
    student_id = int(claims["user_id"])
    profile = get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student or data not found")
    return profile
