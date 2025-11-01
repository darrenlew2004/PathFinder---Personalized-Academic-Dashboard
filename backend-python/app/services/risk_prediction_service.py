from typing import List, Dict
from uuid import UUID
import logging
from app.models import (
    Student, Course, Enrollment, RiskPrediction, 
    RiskLevel, CourseStatus
)
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class RiskPredictionService:
    # Weight factors for risk calculation
    GPA_WEIGHT = 0.35
    ATTENDANCE_WEIGHT = 0.25
    PREREQUISITE_WEIGHT = 0.20
    DIFFICULTY_WEIGHT = 0.20
    
    def predict_risk(
        self,
        student: Student,
        course: Course,
        enrollments: List[Enrollment]
    ) -> RiskPrediction:
        """Predict risk for a student taking a specific course"""
        return self._calculate_risk_prediction(student, course, enrollments)
    
    def predict_risks_for_student(
        self,
        student: Student,
        current_courses: List[Course],
        enrollments: List[Enrollment]
    ) -> List[RiskPrediction]:
        """Predict risks for all courses a student is enrolled in"""
        predictions = []
        for course in current_courses:
            prediction = self._calculate_risk_prediction(student, course, enrollments)
            predictions.append(prediction)
        return predictions
    
    def _calculate_risk_prediction(
        self,
        student: Student,
        course: Course,
        enrollment_history: List[Enrollment]
    ) -> RiskPrediction:
        """Calculate risk prediction based on multiple factors"""
        
        # Calculate individual risk factors
        gpa_factor = self._calculate_gpa_factor(student.gpa)
        attendance_factor = self._calculate_attendance_factor(enrollment_history)
        prerequisite_factor = self._calculate_prerequisite_factor(course, enrollment_history)
        difficulty_factor = self._calculate_difficulty_factor(course.difficulty, student.gpa)
        
        # Calculate weighted risk score (0.0 to 1.0, where 1.0 is highest risk)
        risk_score = (
            gpa_factor * self.GPA_WEIGHT +
            attendance_factor * self.ATTENDANCE_WEIGHT +
            prerequisite_factor * self.PREREQUISITE_WEIGHT +
            difficulty_factor * self.DIFFICULTY_WEIGHT
        )
        
        # Determine risk level
        if risk_score < 0.35:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.65:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(len(enrollment_history), student.semester)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level,
            gpa_factor,
            attendance_factor,
            prerequisite_factor,
            difficulty_factor,
            course
        )
        
        # Predict grade
        predicted_grade = self._predict_grade(risk_score, student.gpa)
        
        factors = {
            "gpa": gpa_factor,
            "attendance": attendance_factor,
            "prerequisites": prerequisite_factor,
            "difficulty": difficulty_factor
        }
        
        return RiskPrediction(
            id=uuid4(),
            student_id=student.id,
            course_id=course.id,
            risk_level=risk_level,
            confidence=confidence,
            factors=factors,
            recommendations=recommendations,
            predicted_grade=predicted_grade,
            created_at=datetime.utcnow()
        )
    
    def _calculate_gpa_factor(self, gpa: float) -> float:
        """Higher GPA = lower risk"""
        # GPA range: 0.0 - 4.0, normalize to risk (inverse)
        return max(0.0, min(1.0, (4.0 - gpa) / 4.0))
    
    def _calculate_attendance_factor(self, enrollments: List[Enrollment]) -> float:
        """Lower attendance = higher risk"""
        if not enrollments:
            return 0.5  # Neutral if no history
        
        avg_attendance = sum(e.attendance_rate for e in enrollments) / len(enrollments)
        return 1.0 - avg_attendance
    
    def _calculate_prerequisite_factor(
        self,
        course: Course,
        enrollments: List[Enrollment]
    ) -> float:
        """Missing prerequisites = higher risk"""
        if not course.prerequisites:
            return 0.0  # No prerequisites = no risk
        
        completed_courses = [
            e for e in enrollments 
            if e.status == CourseStatus.COMPLETED
        ]
        
        # Simplified - in production, would map course IDs to codes
        prerequisites_met = 0
        for prereq in course.prerequisites:
            # This is a simplified check
            prerequisites_met += 1 if any(prereq in str(e.course_id) for e in completed_courses) else 0
        
        completion_rate = prerequisites_met / len(course.prerequisites) if course.prerequisites else 0.0
        return 1.0 - completion_rate
    
    def _calculate_difficulty_factor(self, course_difficulty: float, student_gpa: float) -> float:
        """Risk increases when difficulty exceeds capability"""
        # Difficulty range: 1.0 - 5.0
        normalized_difficulty = (course_difficulty - 1.0) / 4.0  # Normalize to 0.0-1.0
        student_capability = student_gpa / 4.0  # Normalize GPA to 0.0-1.0
        
        # Risk increases when difficulty exceeds capability
        return max(0.0, normalized_difficulty - student_capability)
    
    def _calculate_confidence(self, enrollment_count: int, semester: int) -> float:
        """More historical data = higher confidence"""
        history_factor = min(1.0, enrollment_count / 10.0)
        semester_factor = min(1.0, semester / 8.0)
        return (history_factor + semester_factor) / 2.0
    
    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        gpa_factor: float,
        attendance_factor: float,
        prerequisite_factor: float,
        difficulty_factor: float,
        course: Course
    ) -> List[str]:
        """Generate personalized recommendations based on risk factors"""
        recommendations = []
        
        # Risk level based recommendations
        if risk_level == RiskLevel.HIGH:
            recommendations.append("Consider postponing this course until prerequisites are completed")
            recommendations.append("Speak with your academic advisor about course load")
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("Allocate extra study time for this course")
            recommendations.append("Form a study group with classmates")
        else:  # LOW
            recommendations.append("Maintain current study habits")
            recommendations.append("Consider taking on additional challenging courses")
        
        # Factor-specific recommendations
        if gpa_factor > 0.6:
            recommendations.append("Focus on improving overall GPA through easier electives")
            recommendations.append("Seek tutoring services for challenging subjects")
        
        if attendance_factor > 0.6:
            recommendations.append("Prioritize class attendance - aim for 90%+ attendance rate")
            recommendations.append("Set reminders for all class sessions")
        
        if prerequisite_factor > 0.5:
            recommendations.append(f"Review prerequisite materials: {', '.join(course.prerequisites)}")
            recommendations.append("Consider auditing prerequisite courses if needed")
        
        if difficulty_factor > 0.6:
            recommendations.append("Start studying early and create a structured study schedule")
            recommendations.append("Attend office hours regularly for additional support")
            recommendations.append("Allocate 10-15 hours per week for this course")
        
        return recommendations
    
    def _predict_grade(self, risk_score: float, gpa: float) -> str:
        """Predict grade based on risk score and GPA"""
        score_factor = 1.0 - risk_score
        predicted_score = (score_factor * 0.6 + (gpa / 4.0) * 0.4) * 100
        
        if predicted_score >= 90:
            return "A"
        elif predicted_score >= 85:
            return "A-"
        elif predicted_score >= 80:
            return "B+"
        elif predicted_score >= 75:
            return "B"
        elif predicted_score >= 70:
            return "B-"
        elif predicted_score >= 65:
            return "C+"
        elif predicted_score >= 60:
            return "C"
        elif predicted_score >= 55:
            return "C-"
        elif predicted_score >= 50:
            return "D"
        else:
            return "F"


# Singleton instance
risk_prediction_service = RiskPredictionService()
