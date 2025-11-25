import sys, pathlib
from pprint import pprint

# Ensure root on path
ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.catalog.bcs_programs import load_bcs_variants


def demo():
    variants = load_bcs_variants()
    # Simulate a student who completed first semester of 202301-normal
    completed = {'ENG1044','CSC1202','MTH1114','CSC1024'}
    v = variants['202301-normal']
    progress = v.compute_progress(completed)
    print('Progress report for 202301-normal after S2 assumption:')
    pprint(progress)

    # What-if risk sample (placeholder metrics)
    from backend.app.catalog.program_catalog_models import RiskEngine
    engine = RiskEngine(v)
    planned_codes = ['PRG1203','SEG1201','NET1014']
    student_metrics = {'cgpa':3.2,'attendance':92.0,'gpa_trend':0.1,'planned_credits':0}
    risk_result = engine.what_if(planned_codes, student_metrics, completed)
    print('\nWhat-if risk result:')
    for cr in risk_result.per_course:
        print(cr.subject_code, cr.predicted_risk, cr.numeric_score, cr.factors)
    print('Aggregate:', risk_result.risk_band, risk_result.aggregated_risk_score)

if __name__ == '__main__':
    demo()
