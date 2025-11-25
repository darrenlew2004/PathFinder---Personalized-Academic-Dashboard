from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal, Set

Category = Literal['core','compulsory','choice-core','elective-discipline','elective-free','capstone','internship','placeholder']
RiskBand = Literal['low','medium','high']

@dataclass
class Course:
    subject_code: str
    subject_name: str
    credit: int
    semester_offering: Optional[int] = None
    category: Category = 'core'
    elective_group: Optional[str] = None  # e.g. D1Y2
    prerequisites: List[str] = field(default_factory=list)
    corequisites: List[str] = field(default_factory=list)
    is_placeholder: bool = False

@dataclass
class ChoicePair:
    option_codes: List[str]  # exactly two codes (either requirement)

    def satisfied(self, completed: Set[str]) -> bool:
        return any(code in completed for code in self.option_codes)

@dataclass
class ElectiveGroup:
    group_code: str  # e.g. D1Y2
    year_level: Optional[int]
    options: List[Course] = field(default_factory=list)

@dataclass
class ElectiveSlot:
    group_code: str
    count: int = 1

@dataclass
class SemesterPlan:
    semester_number: int
    required_courses: List[Course] = field(default_factory=list)
    elective_slots: List[ElectiveSlot] = field(default_factory=list)

@dataclass
class ProgressReport:
    completed_credits: int
    total_credits: int
    outstanding_credits: int
    core_remaining: List[str]
    discipline_elective_placeholders_remaining: List[str]
    free_elective_placeholders_remaining: List[str]
    either_pairs_remaining: List[List[str]]
    percent_complete: float

@dataclass
class ProgrammeVariant:
    programme_code: str  # e.g. BCS
    intake_code: str     # e.g. 202301
    entry_type: str      # normal | direct | precalc
    semesters: List[SemesterPlan] = field(default_factory=list)
    elective_groups: Dict[str, ElectiveGroup] = field(default_factory=dict)
    prerequisite_graph: Dict[str, List[str]] = field(default_factory=dict)
    choice_pairs: List[ChoicePair] = field(default_factory=list)
    discipline_elective_placeholders: List[str] = field(default_factory=list)  # e.g. D1Y2, D2Y2...
    free_elective_placeholders: List[str] = field(default_factory=list)       # F1, F2, F3

    def list_all_courses(self) -> List[Course]:
        courses: List[Course] = []
        for sem in self.semesters:
            courses.extend(sem.required_courses)
        # add unique elective group options
        seen: Set[str] = set(c.subject_code for c in courses)
        for eg in self.elective_groups.values():
            for c in eg.options:
                if c.subject_code not in seen:
                    courses.append(c)
                    seen.add(c.subject_code)
        return courses

    def future_courses_for_student(self, completed_codes: Set[str]) -> List[Course]:
        return [c for c in self.list_all_courses() if c.subject_code not in completed_codes and not c.is_placeholder]

    def compute_progress(self, completed_codes: Set[str]) -> ProgressReport:
        all_courses = [c for c in self.list_all_courses() if not c.is_placeholder]
        total_credits = sum(c.credit for c in all_courses)
        completed_credits = sum(c.credit for c in all_courses if c.subject_code in completed_codes)

        core_remaining = [c.subject_code for c in all_courses if c.subject_code not in completed_codes and c.category in ('core','compulsory','capstone','internship')]

        # Elective placeholders remain if no real course substituted yet.
        discipline_remaining = [slot for slot in self.discipline_elective_placeholders if slot not in completed_codes]
        free_remaining = [slot for slot in self.free_elective_placeholders if slot not in completed_codes]

        either_remaining = [cp.option_codes for cp in self.choice_pairs if not cp.satisfied(completed_codes)]

        outstanding_credits = total_credits - completed_credits
        percent_complete = round(completed_credits / total_credits * 100.0, 2) if total_credits else 0.0
        return ProgressReport(
            completed_credits=completed_credits,
            total_credits=total_credits,
            outstanding_credits=outstanding_credits,
            core_remaining=core_remaining,
            discipline_elective_placeholders_remaining=discipline_remaining,
            free_elective_placeholders_remaining=free_remaining,
            either_pairs_remaining=either_remaining,
            percent_complete=percent_complete
        )

@dataclass
class CourseRisk:
    subject_code: str
    subject_name: str
    predicted_risk: RiskBand
    numeric_score: float
    factors: Dict[str, float]

@dataclass
class WhatIfResult:
    selected_subject_codes: List[str]
    total_credits: int
    aggregated_risk_score: float
    risk_band: RiskBand
    per_course: List[CourseRisk]

# Simple rule-based risk computation scaffold
class RiskEngine:
    def __init__(self, programme: ProgrammeVariant):
        self.programme = programme

    def compute_course_risk(self, course: Course, student_metrics: Dict[str, float], completed: Set[str]) -> CourseRisk:
        cgpa = student_metrics.get('cgpa', 0.0)
        avg_attendance = student_metrics.get('attendance', 0.0)
        trend = student_metrics.get('gpa_trend', 0.0)  # -1..1
        workload = student_metrics.get('planned_credits', 0.0)

        prereqs = self.programme.prerequisite_graph.get(course.subject_code, [])
        prereq_completed_ratio = 1.0 if not prereqs else sum(1 for p in prereqs if p in completed) / len(prereqs)

        # Weighted heuristic
        score = (
            0.30 * prereq_completed_ratio +
            0.25 * (cgpa / 4.0) +
            0.15 * ((trend + 1) / 2) +  # normalize -1..1 to 0..1
            0.15 * (avg_attendance / 100.0) +
            0.15 * max(0.0, 1 - (workload / 24.0))  # assume 24 credits is heavy
        )

        if score >= 0.7:
            band: RiskBand = 'low'
        elif score >= 0.4:
            band = 'medium'
        else:
            band = 'high'

        return CourseRisk(
            subject_code=course.subject_code,
            subject_name=course.subject_name,
            predicted_risk=band,
            numeric_score=round(score, 3),
            factors={
                'prereq_completed_ratio': prereq_completed_ratio,
                'cgpa_scaled': cgpa / 4.0,
                'trend_scaled': (trend + 1) / 2,
                'attendance_scaled': avg_attendance / 100.0,
                'workload_penalty': max(0.0, 1 - (workload / 24.0))
            }
        )

    def what_if(self, planned_codes: List[str], student_metrics: Dict[str, float], completed: Set[str]) -> WhatIfResult:
        courses = [c for c in self.programme.list_all_courses() if c.subject_code in planned_codes]
        total_credits = sum(c.credit for c in courses)
        # update workload in metrics
        student_metrics = {**student_metrics, 'planned_credits': total_credits}
        per_course = [self.compute_course_risk(c, student_metrics, completed) for c in courses]
        aggregated = sum(cr.numeric_score for cr in per_course) / len(per_course) if per_course else 0.0
        if aggregated >= 0.7:
            band: RiskBand = 'low'
        elif aggregated >= 0.4:
            band = 'medium'
        else:
            band = 'high'
        return WhatIfResult(planned_codes, total_credits, round(aggregated,3), band, per_course)
