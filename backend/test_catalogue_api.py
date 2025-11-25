import requests
import json

BASE_URL = "http://localhost:9000"

def test_variants():
    print("Testing /api/catalogue/variants...")
    resp = requests.get(f"{BASE_URL}/api/catalogue/variants")
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
    print()

def test_electives():
    print("Testing /api/catalogue/variant/202301-normal/electives...")
    resp = requests.get(f"{BASE_URL}/api/catalogue/variant/202301-normal/electives")
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Groups: {list(data['elective_groups'].keys())}")
    for code, group in list(data['elective_groups'].items())[:2]:
        print(f"\n{code}:")
        for opt in group['options'][:3]:
            print(f"  - {opt['subject_code']}: {opt['subject_name']}")
    print()

def test_progress():
    print("Testing /api/catalogue/progress...")
    payload = {
        "intake": "202301",
        "entry_type": "normal",
        "completed_codes": ["ENG1044", "CSC1202", "MTH1114", "CSC1024"]
    }
    resp = requests.post(f"{BASE_URL}/api/catalogue/progress", json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Completed: {data['completed_credits']}/{data['total_credits']} ({data['percent_complete']}%)")
    print(f"Core remaining: {len(data['core_remaining'])} courses")
    print(f"Discipline electives remaining: {data['discipline_elective_placeholders_remaining']}")
    print()

def test_what_if():
    print("Testing /api/catalogue/what-if...")
    payload = {
        "intake": "202301",
        "entry_type": "normal",
        "planned_codes": ["PRG1203", "SEG1201", "NET1014"],
        "completed_codes": ["ENG1044", "CSC1202", "MTH1114", "CSC1024"],
        "cgpa": 3.2,
        "attendance": 92.0,
        "gpa_trend": 0.1
    }
    resp = requests.post(f"{BASE_URL}/api/catalogue/what-if", json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Total credits: {data['total_credits']}")
    print(f"Aggregated risk: {data['risk_band']} ({data['aggregated_risk_score']})")
    for course in data['per_course']:
        print(f"  {course['subject_code']}: {course['predicted_risk']}")
    print()

if __name__ == '__main__':
    try:
        test_variants()
        test_electives()
        test_progress()
        test_what_if()
        print("✓ All tests passed!")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
