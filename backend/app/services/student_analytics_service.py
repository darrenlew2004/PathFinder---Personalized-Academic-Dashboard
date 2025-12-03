import os
from functools import lru_cache
from typing import Optional, Dict, Any, List

import pandas as pd
import numpy as np

from app.models import StudentProfile, StudentTermStat, SubjectBrief

DATA_PATH = os.environ.get("PF_FLATTENED_CSV", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "flattened_students_subjects.csv"))

GRADE_TO_POINTS: Dict[str, float] = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'D-': 0.7,
    'F': 0.0, 'F*': 0.0, 'F**': 0.0
}
PASS_GRADES = {k for k, v in GRADE_TO_POINTS.items() if v > 0.0}


@lru_cache(maxsize=1)
def _load_df() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        # Return empty DF with expected columns
        cols = [
            'student_id', 'subject_code', 'subject_name', 'coursework_percentage',
            'exam_percentage', 'overall_percentage', 'grade', 'exam_month', 'exam_year', 'status'
        ]
        return pd.DataFrame(columns=cols)

    df = pd.read_csv(DATA_PATH, dtype={
        'student_id': str,
        'subject_code': str,
        'subject_name': str,
        'grade': str,
        'exam_month': 'Int64',
        'exam_year': 'Int64',
    })
    # normalize
    df['overall_percentage'] = pd.to_numeric(df.get('overall_percentage'), errors='coerce')
    df['coursework_percentage'] = pd.to_numeric(df.get('coursework_percentage'), errors='coerce')
    df['exam_percentage'] = pd.to_numeric(df.get('exam_percentage'), errors='coerce')
    df['grade'] = df['grade'].astype(str).str.strip()
    df['term'] = df['exam_year'].astype('Int64').astype(str) + '-' + df['exam_month'].astype('Int64').astype(str).str.zfill(2)
    return df


@lru_cache(maxsize=1)
def _cohort_means() -> pd.DataFrame:
    df = _load_df()
    if df.empty:
        return pd.DataFrame(columns=['subject_code', 'cohort_mean_overall'])
    return (
        df.groupby('subject_code')['overall_percentage']
          .mean()
          .reset_index()
          .rename(columns={'overall_percentage': 'cohort_mean_overall'})
    )


def _subject_brief(row: pd.Series) -> Optional[SubjectBrief]:
    if row is None or row.empty:
        return None
    return SubjectBrief(
        subjectcode=row.get('subject_code'),
        subjectname=row.get('subject_name'),
        overallpercentage=float(row.get('overall_percentage')) if pd.notna(row.get('overall_percentage')) else None
    )


def get_student_profile(student_id: int) -> Optional[StudentProfile]:
    df = _load_df()
    if df.empty:
        return None

    # filter
    df_s = df[df['student_id'].astype(str) == str(student_id)].copy()
    if df_s.empty:
        return None

    # grade points
    df_s['points'] = df_s['grade'].map(GRADE_TO_POINTS)

    # benchmark deltas
    cohort = _cohort_means().set_index('subject_code')
    df_s['benchmark_delta'] = df_s.apply(
        lambda r: (r['overall_percentage'] - cohort.loc[r['subject_code'], 'cohort_mean_overall'])
        if pd.notna(r['overall_percentage']) and r['subject_code'] in cohort.index else np.nan,
        axis=1
    )

    # best/worst subject by overall_percentage
    best_row = df_s.sort_values('overall_percentage', ascending=False).head(1).squeeze()
    worst_row = df_s.sort_values('overall_percentage', ascending=True).head(1).squeeze()

    # term stats
    ts = (
        df_s.groupby('term').agg(
            avg_percentage=('overall_percentage', 'mean'),
            total_exams=('subject_code', 'count'),
            passed=('grade', lambda x: int(x.isin(PASS_GRADES).sum()))
        ).reset_index()
    )
    if not ts.empty:
        ts['pass_rate'] = (ts['passed'] / ts['total_exams'] * 100.0).round(2)
        ts = ts.sort_values('term')
    term_stats: List[StudentTermStat] = [
        StudentTermStat(
            term=str(r['term']),
            avg_percentage=float(r['avg_percentage']) if pd.notna(r['avg_percentage']) else None,
            total_exams=int(r['total_exams']),
            pass_rate=float(r['pass_rate']) if pd.notna(r.get('pass_rate')) else None
        ) for _, r in ts.iterrows()
    ]

    # trend per term (simple linear slope)
    slope_val: Optional[float] = None
    if df_s['overall_percentage'].notna().sum() >= 2:
        # create ordinal index for terms - only use rows with valid overall_percentage
        df_valid = df_s[df_s['overall_percentage'].notna()].copy()
        order = {t: i for i, t in enumerate(sorted(df_valid['term'].dropna().unique()))}
        x = df_valid['term'].map(order).to_numpy()
        y = df_valid['overall_percentage'].to_numpy()
        # Filter out any remaining NaN
        mask = ~(np.isnan(x) | np.isnan(y))
        x, y = x[mask], y[mask]
        if len(x) >= 2:
            try:
                coeffs = np.polyfit(x, y, 1)
                slope_val = float(coeffs[0]) if not np.isnan(coeffs[0]) else None
            except Exception:
                slope_val = None

    profile = StudentProfile(
        student_id=int(student_id),
        subjects_taken=int(len(df_s)),
        terms_taken=int(df_s['term'].nunique()),
        current_gpa=float(df_s['points'].dropna().mean()) if df_s['points'].notna().any() else None,
        avg_score=float(df_s['overall_percentage'].mean()) if df_s['overall_percentage'].notna().any() else None,
        score_std=float(df_s['overall_percentage'].std()) if df_s['overall_percentage'].notna().sum() >= 2 else None,
        best_subject=_subject_brief(best_row) if isinstance(best_row, pd.Series) else None,
        worst_subject=_subject_brief(worst_row) if isinstance(worst_row, pd.Series) else None,
        avg_benchmark_delta=float(df_s['benchmark_delta'].mean()) if df_s['benchmark_delta'].notna().any() else None,
        fails_count=int(df_s['points'].fillna(999).eq(0.0).sum()),
        retakes_count=int((df_s.groupby('subject_code').size() > 1).sum()),
        score_trend_per_term=slope_val,
        term_stats=term_stats
    )

    return profile
