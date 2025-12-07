"""
Subject Success Prediction Service

Predicts whether a student will pass or struggle with a subject based on:
1. Performance in prerequisite/related subjects
2. Historical cohort performance patterns
3. Subject difficulty metrics
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from functools import lru_cache

# Grade to GPA mapping
GRADE_POINTS = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'D-': 0.7,
    'E': 0.5, 'F': 0.0, 'F*': 0.0,
    'P': None,  # Pass (no grade points)
    'EX': None,  # Exemption
    'INC': None,  # Incomplete
    'W': None,   # Withdrawn
}

# Subject prerequisite/dependency chains
# Format: target_subject -> [(prereq_code, weight), ...]
# Weight indicates how strongly the prereq impacts the target (0.0-1.0)
SUBJECT_PREREQUISITES = {
    # Database chain
    'SEG2102': [('SEG1201', 0.9)],  # DatabaseManagementSystems <- DatabaseFundamentals
    'CSC3064': [('SEG2102', 0.8), ('SEG1201', 0.5)],  # DatabaseEngineering <- DBMS, DBFundamentals
    'BIS2216': [('SEG1201', 0.6)],  # DataMining <- DatabaseFundamentals
    'BIS3216': [('BIS2216', 0.8), ('SEG1201', 0.4)],  # DataMiningKnowledgeDiscovery <- DataMiningFund
    
    # Programming chain
    'PRG1203': [('CSC1024', 0.9)],  # OOP Fundamentals <- Programming Principles
    'PRG2104': [('PRG1203', 0.9), ('CSC1024', 0.4)],  # OOP <- OOP Fundamentals
    'CSC2103': [('PRG1203', 0.8), ('CSC1024', 0.5)],  # Data Structures <- OOP Fund, Programming
    'CSC2044': [('PRG2104', 0.7), ('PRG1203', 0.5)],  # Concurrent Programming <- OOP
    'PRG2205': [('PRG2104', 0.7), ('CSC2103', 0.5)],  # Programming Languages <- OOP, DS
    'PRG2214': [('PRG1203', 0.7), ('CSC1024', 0.5)],  # Functional Programming <- OOP Fund
    
    # Software Engineering chain
    'SEG2202': [('PRG1203', 0.6), ('SEG1201', 0.5)],  # Software Engineering <- OOP Fund, DB
    'CSC3209': [('SEG2202', 0.8), ('PRG2104', 0.6)],  # Software Architecture <- SE, OOP
    'PRG3014': [('SEG2202', 0.5), ('CSC3024', 0.6)],  # UI/UX <- SE, HCI
    
    # AI/ML chain
    'CSC3206': [('CSC2103', 0.7), ('MTH1114', 0.5)],  # AI <- DS&A, Math
    'CSC3034': [('CSC3206', 0.8), ('CSC2103', 0.4)],  # Computational Intelligence <- AI, DS&A
    'CSC3014': [('CSC2014', 0.7), ('CSC3206', 0.5)],  # Computer Vision <- Digital Image, AI
    'CSC2014': [('MTH1114', 0.5), ('CSC1024', 0.4)],  # Digital Image Processing <- Math, Programming
    
    # Networking chain
    'NET2201': [('NET1014', 0.9)],  # Computer Networks <- Networking Principles
    'NET2102': [('NET1014', 0.8)],  # Data Communications <- Networking Principles
    'NET2103': [('NET2201', 0.7), ('CSC2104', 0.5)],  # Network & System Admin <- Networks, OS
    'NET3014': [('NET2201', 0.8), ('NET2102', 0.5)],  # Advanced Networks <- Networks, DataComm
    'NET3106': [('NET2201', 0.7), ('CSC3044', 0.6)],  # Network Security <- Networks, Security
    'NET3204': [('NET2201', 0.7), ('CSC2104', 0.5)],  # Distributed Systems <- Networks, OS
    'NET3207': [('NET2201', 0.8), ('NET2103', 0.6)],  # Network Management <- Networks, Admin
    'MMD3105': [('NET2201', 0.6)],  # Multimedia Networking <- Networks
    
    # Security chain
    'CSC3044': [('NET2201', 0.6), ('CSC2104', 0.5)],  # Computer Security <- Networks, OS
    'SEC3024': [('CSC3044', 0.8), ('NET2201', 0.5)],  # CEH <- Security, Networks
    'SEC3014': [('NET3106', 0.8), ('CSC3044', 0.5)],  # Advanced Network Security
    'SEC3034': [('SEC3024', 0.7), ('CSC3044', 0.6)],  # Forensic Investigator <- CEH, Security
    'SEC3044': [('CSC3044', 0.8), ('SEC3024', 0.6)],  # Advanced Security Topics
    
    # Operating Systems chain  
    'CSC2104': [('CSC1202', 0.7), ('CSC1024', 0.5)],  # OS Fundamentals <- Comp Org, Programming
    'OSS1014': [('CSC1202', 0.7), ('CSC1024', 0.5)],  # OS Fundamentals (alt code)
    
    # Web chain
    'WEB2202': [('WEB1201', 0.9), ('PRG1203', 0.5)],  # Web Programming <- Web Fund, OOP
    
    # Math chain
    'MTH2103': [('MTH1114', 0.8), ('IST1024', 0.5)],  # Probability & Stats <- Math, Intro Stats
    'IST2024': [('IST1024', 0.7), ('MTH1114', 0.4)],  # Applied Statistics <- Intro Stats, Math
    
    # Analytics chain
    'IST2334': [('SEG1201', 0.5), ('NET1014', 0.4)],  # Web & Network Analytics
    'IST2134': [('IST1024', 0.5)],  # Social Media Analytics
    'IST2234': [('IST1024', 0.6), ('IST2034', 0.5)],  # Visual Analytics
    'IST3134': [('SEG2102', 0.6), ('IST2024', 0.5)],  # Big Data Analytics
    'IST3144': [('IST2024', 0.7)],  # Problem Solving Analytics
    'IST3244': [('IST2024', 0.8), ('IST2234', 0.5)],  # Advanced Business Analytics
    'BIS3218': [('BIS2216', 0.7), ('SEG2102', 0.5)],  # Business Intelligence
    
    # Project chain
    'PRJ3213': [('SEG2202', 0.6), ('PRG2104', 0.5)],  # Capstone 1 <- SE, OOP
    'PRJ3223': [('PRJ3213', 0.9)],  # Capstone 2 <- Capstone 1
    
    # HCI
    'CSC3024': [('SEG2202', 0.4), ('PRG1203', 0.4)],  # HCI <- SE, OOP Fund
}

# Risk thresholds
RISK_THRESHOLDS = {
    'high': 2.0,    # Below C grade in prereqs = high risk
    'medium': 2.7,  # C+ to B- range = medium risk
    'low': 3.3,     # B+ and above = low risk
}


@dataclass
class PrerequisitePerformance:
    """Performance in a single prerequisite subject"""
    subject_code: str
    subject_name: str
    grade: str
    grade_points: float
    weight: float
    impact_score: float  # grade_points * weight


@dataclass 
class SubjectPrediction:
    """Prediction for a single subject"""
    subject_code: str
    subject_name: str
    risk_level: str  # 'low', 'medium', 'high', 'very_high'
    predicted_success_probability: float  # 0.0 - 1.0
    weighted_prereq_gpa: float
    prereq_performance: List[PrerequisitePerformance]
    missing_prereqs: List[str]
    recommendation: str
    cohort_pass_rate: Optional[float] = None
    cohort_avg_score: Optional[float] = None
    # ML-based predictions (hybrid approach)
    ml_probability: Optional[float] = None  # ML model prediction
    ml_confidence: Optional[float] = None  # ML confidence score
    ml_top_factors: Optional[List[tuple]] = None  # Top contributing factors
    prediction_method: str = 'rule-based'  # 'rule-based', 'ml', or 'hybrid'


@dataclass
class StudentPredictionReport:
    """Full prediction report for a student's planned subjects"""
    student_id: int
    current_gpa: float
    predictions: List[SubjectPrediction] = field(default_factory=list)
    high_risk_subjects: List[str] = field(default_factory=list)
    recommended_order: List[str] = field(default_factory=list)


class SubjectPredictionService:
    """Service for predicting student success in subjects (Hybrid: Rule-based + ML)"""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.cohort_stats: Dict[str, Dict] = {}
        self.ml_service = None
        self._load_data()
        self._load_ml_service()
    
    def _load_data(self):
        """Load the flattened student data"""
        data_path = Path(__file__).parent.parent.parent / 'data' / 'flattened_students_subjects.csv'
        if data_path.exists():
            self.df = pd.read_csv(data_path)
            self._compute_cohort_stats()
    
    def _load_ml_service(self):
        """Load ML prediction service for hybrid predictions"""
        try:
            from .ml_prediction_service import get_ml_prediction_service
            self.ml_service = get_ml_prediction_service()
        except Exception as e:
            print(f"⚠ ML service not available: {e}")
            self.ml_service = None
    
    def _compute_cohort_stats(self):
        """Compute cohort-level statistics for each subject"""
        if self.df is None:
            return
            
        # Filter to graded subjects only
        graded = self.df[self.df['grade'].notna() & ~self.df['grade'].isin(['P', 'EX', 'INC', 'W', '-'])]
        
        for code in graded['subject_code'].unique():
            subject_data = graded[graded['subject_code'] == code]
            
            # Calculate pass rate (C or better)
            passing_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
            passed = subject_data[subject_data['grade'].isin(passing_grades)]
            pass_rate = len(passed) / len(subject_data) if len(subject_data) > 0 else 0
            
            # Calculate average score
            valid_scores = subject_data['overall_percentage'].dropna()
            avg_score = valid_scores.mean() if len(valid_scores) > 0 else None
            
            # Calculate average GPA
            gpas = []
            for grade in subject_data['grade']:
                if grade in GRADE_POINTS and GRADE_POINTS[grade] is not None:
                    gpas.append(GRADE_POINTS[grade])
            avg_gpa = np.mean(gpas) if gpas else None
            
            self.cohort_stats[code] = {
                'pass_rate': pass_rate,
                'avg_score': avg_score,
                'avg_gpa': avg_gpa,
                'total_students': len(subject_data),
                'subject_name': subject_data['subject_name'].iloc[0] if len(subject_data) > 0 else code
            }
    
    def _get_grade_points(self, grade: str) -> Optional[float]:
        """Convert grade to grade points"""
        if not grade:
            return None
        grade = str(grade).strip().upper()
        # Handle special cases like F*, D**, C*
        clean_grade = grade.rstrip('*')
        return GRADE_POINTS.get(clean_grade, GRADE_POINTS.get(grade))
    
    def _calculate_student_performance_features(self, student_id: int, student_subjects: Dict[str, Dict]) -> Dict:
        """Calculate student performance features for ML model"""
        if not student_subjects:
            return {
                'num_subjects_completed': 0,
                'current_gpa': 0.0,
                'gpa_trend_last_3': 0.0,
                'avg_coursework_percentage': 0.0,
                'avg_overall_percentage': 0.0,
                'num_fails': 0,
                'fail_rate': 0.0
            }
        
        # Calculate current GPA
        gpas = [s['grade_points'] for s in student_subjects.values() if s['grade_points'] is not None]
        current_gpa = np.mean(gpas) if gpas else 0.0
        
        # GPA trend (last 3 vs previous 3)
        gpa_trend = 0.0
        if len(gpas) >= 6:
            recent_3 = np.mean(gpas[-3:])
            previous_3 = np.mean(gpas[-6:-3])
            gpa_trend = recent_3 - previous_3
        
        # Average percentages
        percentages = [s['overall_percentage'] for s in student_subjects.values() if s.get('overall_percentage') is not None]
        avg_overall = np.mean(percentages) if percentages else 0.0
        
        # Fail count
        failing_grades = ['D+', 'D', 'D-', 'E', 'F', 'F*']
        num_fails = sum(1 for s in student_subjects.values() if s['grade'] in failing_grades)
        fail_rate = num_fails / len(student_subjects) if student_subjects else 0.0
        
        return {
            'num_subjects_completed': len(student_subjects),
            'current_gpa': current_gpa,
            'gpa_trend_last_3': gpa_trend,
            'avg_coursework_percentage': 0.0,  # Not available in current data
            'avg_overall_percentage': avg_overall,
            'num_fails': num_fails,
            'fail_rate': fail_rate
        }
    
    def _get_student_subjects(self, student_id: int) -> Dict[str, Dict]:
        """Get all subjects taken by a student with their grades (with LRU caching)"""
        # Initialize cache if needed
        if not hasattr(self, '_student_cache'):
            self._student_cache = {}
        if not hasattr(self, '_student_perf_cache'):
            self._student_perf_cache = {}
        
        # Check cache first
        if student_id in self._student_cache:
            return self._student_cache[student_id]
        
        if self.df is None:
            return {}
        
        student_data = self.df[self.df['student_id'] == student_id]
        subjects = {}
        
        for _, row in student_data.iterrows():
            code = row['subject_code']
            grade = row['grade']
            gp = self._get_grade_points(grade)
            
            subjects[code] = {
                'subject_code': code,
                'subject_name': row['subject_name'],
                'grade': grade,
                'grade_points': gp,
                'overall_percentage': row['overall_percentage'],
                'status': row.get('status', '')
            }
        
        # LRU-style caching: Remove oldest if cache is full
        if len(self._student_cache) >= 500:  # Increased from 100 to 500
            # Remove 20% oldest entries
            items = list(self._student_cache.items())
            self._student_cache = dict(items[100:])
        
        self._student_cache[student_id] = subjects
        return subjects
    
    def _get_cached_student_performance(self, student_id: int, student_subjects: Dict[str, Dict]) -> Dict:
        """Get cached student performance features or calculate and cache"""
        if not hasattr(self, '_student_perf_cache'):
            self._student_perf_cache = {}
        
        if student_id in self._student_perf_cache:
            return self._student_perf_cache[student_id]
        
        # Calculate and cache
        perf = self._calculate_student_performance_features(student_id, student_subjects)
        
        # LRU-style caching
        if len(self._student_perf_cache) >= 500:
            items = list(self._student_perf_cache.items())
            self._student_perf_cache = dict(items[100:])
        
        self._student_perf_cache[student_id] = perf
        return perf
    
    def _predict_with_subjects(
        self, 
        student_id: int, 
        target_subject_code: str,
        student_subjects: Dict[str, Dict],
        precomputed_ml: Optional[any] = None
    ) -> SubjectPrediction:
        """Internal prediction method that accepts pre-fetched student subjects and optional precomputed ML prediction"""
        prereqs = SUBJECT_PREREQUISITES.get(target_subject_code, [])
        
        prereq_performance = []
        missing_prereqs = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Analyze prerequisite performance
        for prereq_code, weight in prereqs:
            if prereq_code in student_subjects:
                subj = student_subjects[prereq_code]
                gp = subj['grade_points']
                
                if gp is not None:
                    impact = gp * weight
                    prereq_performance.append(PrerequisitePerformance(
                        subject_code=prereq_code,
                        subject_name=subj['subject_name'],
                        grade=subj['grade'],
                        grade_points=gp,
                        weight=weight,
                        impact_score=impact
                    ))
                    total_weighted_score += impact
                    total_weight += weight
            else:
                missing_prereqs.append(prereq_code)
        
        # Calculate weighted prerequisite GPA
        weighted_prereq_gpa = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Get cohort stats for context
        cohort = self.cohort_stats.get(target_subject_code, {})
        cohort_pass_rate = cohort.get('pass_rate')
        cohort_avg_score = cohort.get('avg_score')
        subject_name = cohort.get('subject_name', target_subject_code)
        
        # Calculate success probability
        if total_weight == 0:
            # No prereq data - use cohort average or default
            if cohort_pass_rate is not None:
                success_prob = cohort_pass_rate
            else:
                success_prob = 0.7  # Default moderate probability
            risk_level = 'unknown'
        else:
            # Base probability from prereq performance
            # GPA 4.0 -> 95% success, GPA 2.0 -> 50% success, GPA 0 -> 20% success
            success_prob = 0.2 + (weighted_prereq_gpa / 4.0) * 0.75
            
            # Adjust based on cohort difficulty
            if cohort_pass_rate is not None:
                # If subject is historically difficult, reduce probability
                difficulty_factor = cohort_pass_rate  # 0-1
                success_prob = success_prob * 0.7 + difficulty_factor * 0.3
            
            # Determine risk level
            if weighted_prereq_gpa >= RISK_THRESHOLDS['low']:
                risk_level = 'low'
            elif weighted_prereq_gpa >= RISK_THRESHOLDS['medium']:
                risk_level = 'medium'
            elif weighted_prereq_gpa >= RISK_THRESHOLDS['high']:
                risk_level = 'high'
            else:
                risk_level = 'very_high'
        
        # Adjust for missing prereqs
        if missing_prereqs:
            success_prob *= 0.8  # 20% penalty for missing prereqs
            if risk_level == 'low':
                risk_level = 'medium'
            elif risk_level == 'medium':
                risk_level = 'high'
        
        # === HYBRID APPROACH: Get ML prediction if available ===
        ml_probability = None
        ml_confidence = None
        ml_top_factors = None
        prediction_method = 'rule-based'
        
        # Use precomputed ML result if provided (batch mode), otherwise compute individually
        ml_pred = precomputed_ml
        
        if ml_pred is None and self.ml_service and self.ml_service.is_available():
            # Calculate student performance features (with caching)
            student_features = self._get_cached_student_performance(student_id, student_subjects)
            
            # Prepare prerequisite features for ML
            prereq_features = {
                'num_prerequisites': len(prereqs),
                'num_prerequisites_completed': len(prereq_performance),
                'num_prerequisites_missing': len(missing_prereqs),
                'avg_prereq_grade_points': np.mean([p.grade_points for p in prereq_performance]) if prereq_performance else 0.0,
                'weighted_prereq_gpa': weighted_prereq_gpa,
                'min_prereq_grade': min([p.grade_points for p in prereq_performance]) if prereq_performance else 0.0,
                'max_prereq_grade': max([p.grade_points for p in prereq_performance]) if prereq_performance else 0.0,
            }
            
            # Prepare cohort features for ML
            cohort_features = {
                'subject_pass_rate': cohort_pass_rate if cohort_pass_rate is not None else 0.5,
                'subject_avg_score': cohort_avg_score if cohort_avg_score is not None else 50.0,
                'subject_avg_gpa': cohort.get('avg_gpa', 2.0),
                'subject_total_students': cohort.get('total_students', 0),
            }
            
            # Get ML prediction
            ml_pred = self.ml_service.predict(
                student_features=student_features,
                prereq_features=prereq_features,
                cohort_features=cohort_features,
                subject_code=target_subject_code
            )
        
        if ml_pred:
            ml_probability = ml_pred.success_probability
            ml_confidence = ml_pred.confidence
            ml_top_factors = ml_pred.top_factors
            prediction_method = 'hybrid'
            
            # Use ML prediction as primary, adjust rule-based as secondary
            # Weighted average: 70% ML + 30% rule-based
            success_prob = ml_probability * 0.7 + success_prob * 0.3
            risk_level = ml_pred.risk_level
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            risk_level, weighted_prereq_gpa, prereq_performance, missing_prereqs, subject_name
        )
        
        # Add ML insights to recommendation if available
        if ml_probability is not None and ml_top_factors:
            ml_insight = f"\n\n🤖 ML Analysis (Confidence: {ml_confidence*100:.0f}%): "
            ml_insight += f"Success probability {ml_probability*100:.0f}%. "
            ml_insight += f"Key factors: {', '.join([f[0] for f in ml_top_factors[:3]])}."
            recommendation += ml_insight
        
        return SubjectPrediction(
            subject_code=target_subject_code,
            subject_name=subject_name,
            risk_level=risk_level,
            predicted_success_probability=min(max(success_prob, 0.0), 1.0),
            weighted_prereq_gpa=weighted_prereq_gpa,
            prereq_performance=prereq_performance,
            missing_prereqs=missing_prereqs,
            recommendation=recommendation,
            cohort_pass_rate=cohort_pass_rate,
            cohort_avg_score=cohort_avg_score,
            ml_probability=ml_probability,
            ml_confidence=ml_confidence,
            ml_top_factors=ml_top_factors,
            prediction_method=prediction_method
        )
    
    def _generate_recommendation(
        self,
        risk_level: str,
        weighted_gpa: float,
        prereq_performance: List[PrerequisitePerformance],
        missing_prereqs: List[str],
        subject_name: str
    ) -> str:
        """Generate a personalized recommendation"""
        
        if risk_level == 'very_high':
            weak_prereqs = [p for p in prereq_performance if p.grade_points < 2.0]
            if weak_prereqs:
                weak_names = ', '.join([p.subject_name for p in weak_prereqs[:2]])
                return f"⚠️ High risk. Your performance in {weak_names} suggests you may struggle. Consider reviewing fundamental concepts or seeking tutoring before taking {subject_name}."
            return f"⚠️ High risk. Consider strengthening your foundation before attempting {subject_name}."
        
        elif risk_level == 'high':
            weak_prereqs = [p for p in prereq_performance if p.grade_points < 2.5]
            if weak_prereqs:
                weak_names = ', '.join([p.subject_name for p in weak_prereqs[:2]])
                return f"🔶 Moderate-high risk. Your {weak_names} grade(s) indicate potential challenges. Extra study effort recommended for {subject_name}."
            if missing_prereqs:
                return f"🔶 Some prerequisite subjects not yet taken. Ensure you complete them before {subject_name}."
            return f"🔶 Moderate-high risk. Plan extra study time for {subject_name}."
        
        elif risk_level == 'medium':
            return f"🟡 Moderate risk. You have adequate preparation but should maintain consistent effort in {subject_name}."
        
        elif risk_level == 'low':
            strong_prereqs = [p for p in prereq_performance if p.grade_points >= 3.3]
            if strong_prereqs:
                return f"✅ Good preparation! Your strong performance in prerequisites suggests you're well-prepared for {subject_name}."
            return f"✅ Low risk. You should do well in {subject_name} based on your background."
        
        else:  # unknown
            if missing_prereqs:
                return f"ℹ️ No prerequisite data available. Complete prerequisites first: {', '.join(missing_prereqs)}"
            return f"ℹ️ Limited data to make prediction. This may be an entry-level subject."
    
    def predict_multiple_subjects(
        self, 
        student_id: int, 
        target_subject_codes: List[str]
    ) -> StudentPredictionReport:
        """Predict success for multiple subjects (optimized with batch inference and caching)"""
        
        # Fetch student subjects once for all predictions (cached)
        student_subjects = self._get_student_subjects(student_id)
        
        # Calculate current GPA
        gpas = [s['grade_points'] for s in student_subjects.values() if s['grade_points'] is not None]
        current_gpa = np.mean(gpas) if gpas else 0.0
        
        # Use cached student performance features
        student_features = self._get_cached_student_performance(student_id, student_subjects)
        
        # Batch ML inference if available
        ml_predictions_map = {}
        if self.ml_service and self.ml_service.is_available():
            batch_data = []
            for code in target_subject_codes:
                prereqs = SUBJECT_PREREQUISITES.get(code, [])
                
                # Calculate prereq features
                prereq_performance = []
                missing_prereqs = []
                total_weighted_score = 0.0
                total_weight = 0.0
                
                for prereq_code, weight in prereqs:
                    if prereq_code in student_subjects:
                        subj = student_subjects[prereq_code]
                        gp = subj['grade_points']
                        if gp is not None:
                            prereq_performance.append((prereq_code, gp, weight))
                            total_weighted_score += gp * weight
                            total_weight += weight
                    else:
                        missing_prereqs.append(prereq_code)
                
                weighted_prereq_gpa = total_weighted_score / total_weight if total_weight > 0 else 0.0
                
                prereq_features = {
                    'num_prerequisites': len(prereqs),
                    'num_prerequisites_completed': len(prereq_performance),
                    'num_prerequisites_missing': len(missing_prereqs),
                    'avg_prereq_grade_points': np.mean([p[1] for p in prereq_performance]) if prereq_performance else 0.0,
                    'weighted_prereq_gpa': weighted_prereq_gpa,
                    'min_prereq_grade': min([p[1] for p in prereq_performance]) if prereq_performance else 0.0,
                    'max_prereq_grade': max([p[1] for p in prereq_performance]) if prereq_performance else 0.0,
                }
                
                cohort = self.cohort_stats.get(code, {})
                cohort_features = {
                    'subject_pass_rate': cohort.get('pass_rate') if cohort.get('pass_rate') is not None else 0.5,
                    'subject_avg_score': cohort.get('avg_score') if cohort.get('avg_score') is not None else 50.0,
                    'subject_avg_gpa': cohort.get('avg_gpa', 2.0),
                    'subject_total_students': cohort.get('total_students', 0),
                }
                
                batch_data.append({
                    'student_features': student_features,
                    'prereq_features': prereq_features,
                    'cohort_features': cohort_features,
                    'subject_code': code
                })
            
            # Single batch ML inference call for all subjects
            ml_results = self.ml_service.predict_batch(batch_data)
            ml_predictions_map = {code: result for code, result in zip(target_subject_codes, ml_results)}
        
        # Generate predictions with pre-computed ML results
        predictions = []
        for code in target_subject_codes:
            pred = self._predict_with_subjects(
                student_id, code, student_subjects, 
                precomputed_ml=ml_predictions_map.get(code)
            )
            predictions.append(pred)
        
        # Identify high-risk subjects
        high_risk = [p.subject_code for p in predictions if p.risk_level in ('high', 'very_high')]
        
        # Recommend order (lower risk first)
        risk_order = {'low': 0, 'medium': 1, 'high': 2, 'very_high': 3, 'unknown': 1}
        sorted_preds = sorted(predictions, key=lambda p: risk_order.get(p.risk_level, 2))
        recommended_order = [p.subject_code for p in sorted_preds]
        
        return StudentPredictionReport(
            student_id=student_id,
            current_gpa=current_gpa,
            predictions=predictions,
            high_risk_subjects=high_risk,
            recommended_order=recommended_order
        )
    
    def get_prerequisite_chain(self, subject_code: str) -> Dict:
        """Get the full prerequisite chain for a subject"""
        prereqs = SUBJECT_PREREQUISITES.get(subject_code, [])
        chain = {
            'subject_code': subject_code,
            'subject_name': self.cohort_stats.get(subject_code, {}).get('subject_name', subject_code),
            'direct_prerequisites': [],
            'full_chain': []
        }
        
        visited = set()
        
        def traverse(code: str, depth: int = 0):
            if code in visited or depth > 5:
                return
            visited.add(code)
            
            prereq_list = SUBJECT_PREREQUISITES.get(code, [])
            for prereq_code, weight in prereq_list:
                prereq_name = self.cohort_stats.get(prereq_code, {}).get('subject_name', prereq_code)
                
                if depth == 0:
                    chain['direct_prerequisites'].append({
                        'code': prereq_code,
                        'name': prereq_name,
                        'weight': weight
                    })
                
                chain['full_chain'].append({
                    'code': prereq_code,
                    'name': prereq_name,
                    'depth': depth + 1
                })
                
                traverse(prereq_code, depth + 1)
        
        traverse(subject_code)
        return chain
    
    def predict_subject_success(
        self, 
        student_id: int, 
        target_subject_code: str
    ) -> SubjectPrediction:
        """Predict success probability for a specific subject"""
        student_subjects = self._get_student_subjects(student_id)
        return self._predict_with_subjects(student_id, target_subject_code, student_subjects)


# Singleton instance
_prediction_service: Optional[SubjectPredictionService] = None

def get_prediction_service() -> SubjectPredictionService:
    """Get or create the prediction service singleton"""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = SubjectPredictionService()
    return _prediction_service
