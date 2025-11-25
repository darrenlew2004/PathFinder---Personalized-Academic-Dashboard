from dataclasses import dataclass
from typing import Dict, List, Set

from .program_catalog_models import ProgrammeVariant, SemesterPlan, Course, ChoicePair
from .bcs_electives import build_elective_groups

# Helper to create a course
def c(code: str, name: str, credit: int, sem: int, category: str = 'core', placeholder: bool=False) -> Course:
    return Course(subject_code=code, subject_name=name, credit=credit, semester_offering=sem, category=category, is_placeholder=placeholder)

# Either-subject pair codes common across variants
EITHER_PAIRS = [
    ['MPU3193','MPU3203'],  # Falsafah / Appreciation Ethics
    ['MPU3183','MPU3213'],  # Penghayatan / Malay Communication
]

# Discipline elective placeholder codes by year groups (as per Scala naming)
DISC_ELECTIVE_CODES = ['D1Y2','D2Y2','D4Y3','D5Y3']
FREE_ELECTIVE_CODES = ['*F1','*F2','*F3']

# Map placeholder to readable name
PLACEHOLDER_NAMES = {
    'D1Y2':'Discipline Elective Y2 Slot 1',
    'D2Y2':'Discipline Elective Y2 Slot 2',
    'D4Y3':'Discipline Elective Y3 Slot 1',
    'D5Y3':'Discipline Elective Y3 Slot 2',
    '*F1':'Free Elective 1',
    '*F2':'Free Elective 2',
    '*F3':'Free Elective 3'
}

# Variants to build (subset from Scala file provided)
VARIANT_SPECS = [
    ('202301','normal', False),
    ('202301','precalc', True),
    ('202301','direct', False),
    ('202304','normal', False),
    ('202304','precalc', True),
    ('202304','direct', False),
    ('202309','normal', False),
    ('202309','precalc', True),
]

# Core curriculum per variant (simplified: differences in early semesters & ordering) - extracted from Scala snippet
# For brevity we define common pools and then assemble per variant.
COMMON_COURSES = {
    'ENG1044': ('EnglishforComputerTechnologyStudies',4),
    'CSC1202': ('ComputerOrganisation',4),
    'MTH1114': ('ComputerMathematics',4),
    'CSC1024': ('ProgrammingPrinciples',4),
    'PRG1203': ('Object-OrientedProgrammingFundamentals',4),
    'SEG1201': ('DatabaseFundamentals',4),
    'NET1014': ('NetworkingPrinciples',4),
    'WEB1201': ('WebFundamentals',4),
    'CSC2104': ('OperatingSystemFundamentals',4),
    'SEG2202': ('SoftwareEngineering',4),
    'CSC2103': ('DataStructures&Algorithms',4),
    'PRG2104': ('Object-OrientedProgramming',4),
    'ENG2042': ('CommunicationSkills',2),
    'ENG2044': ('CommunicationSkills',4),
    'CSC2014': ('DigitalImageProcessing',4),
    'NET2201': ('ComputerNetworks',4),
    'CSC3024': ('HumanComputerInteraction',4),
    'SEG3203': ('Internship',6),
    'CSC3206': ('ArtificialIntelligence',4),
    'PRJ3213': ('CapstoneProject1',3),
    'PRJ3223': ('CapstoneProject2',3),
    'NET3204': ('DistributedSystems',4),
    'MAT1013': ('Micro-credentialinComputerMathematicsFundamentals',4),
    'OSS1014': ('OperatingSystemFundamentals',4),
    'BIS2212(MU32422)': ('SocialandProfessionalResponsibilities',2),
    'ENG2042(MU22812)': ('CommunicationSkills',2),
    'MU42422': ('CommunityService',2),
    'MPU2012': ('EntrepreneurialMindsetandSkills',2),
    'MPU3422': ('CommunityServiceforPlanetaryHealth',2),
    'MPU3332': ('IntegrityandAntiCorruption(KIAR)',2),
}

# Variant-specific semester mapping (code -> semester) approximated from Scala listing.
SEM_MAPPING: Dict[str, Dict[str,int]] = {
    '202301-normal': {
        'ENG1044':2,'CSC1202':2,'MTH1114':2,'CSC1024':2,
        'PRG1203':3,'SEG1201':3,'NET1014':3,'WEB1201':3,
        'CSC2104':5,'SEG2202':5,'CSC2103':5,'PRG2104':5,'ENG2042(MU22812)':5,
        'CSC2014':6,'NET2201':6,'CSC3024':6,
        'CSC3206':8,'PRJ3213':8,'MU42422':8,
        'PRJ3223':9,'NET3204':9,'SEG3203':7,
        'BIS2212(MU32422)':4,
    },
    '202301-precalc': {
        'MAT1013':1,
        'ENG1044':2,'CSC1202':2,'CSC1024':2,'NET1014':2,
        'MTH1114':3,'PRG1203':3,'SEG1201':3,'WEB1201':3,
        'CSC2104':5,'SEG2202':5,'CSC2103':5,'PRG2104':5,'ENG2042(MU22812)':5,
        'CSC2014':6,'NET2201':6,'CSC3024':6,
        'CSC3206':8,'PRJ3213':8,'MU42422':8,
        'PRJ3223':9,'NET3204':9,'SEG3203':7,
        'BIS2212(MU32422)':4,
    },
    '202301-direct': {
        'ENG1044':2,'CSC1202':2,'MTH1114':2,'CSC1024':2,
        'PRG1203':3,'SEG1201':3,'NET1014':3,'WEB1201':3,
        'CSC2104':4,'SEG2202':5,'CSC2103':5,'PRG2104':5,'ENG2042(MU22812)':5,
        'CSC2014':6,'NET2201':5,'CSC3024':5,
        'CSC3206':8,'PRJ3213':8,'MU42422':4,
        'PRJ3223':8,'NET3204':8,'SEG3203':9,
        'BIS2212(MU32422)':4,
    },
    '202304-normal': {
        'ENG1044':1,'CSC1202':1,'MTH1114':1,'CSC1024':1,
        'PRG1203':2,'SEG1201':2,'WEB1201':2,'OSS1014':2,
        'NET1014':3,
        'CSC2014':4,'CSC2103':4,'PRG2104':4,'ENG2044':4,
        'CSC3206':7,'PRJ3213':7,'PRJ3223':8,'NET3204':8,'SEG3203':9,
    },
    '202304-precalc': {
        'MAT1013':1,'ENG1044':1,'CSC1202':1,'CSC1024':1,'WEB1201':1,
        'MTH1114':2,'PRG1203':2,'SEG1201':2,'OSS1014':2,
        'NET1014':3,
        'CSC2014':4,'CSC2103':4,'PRG2104':4,'ENG2044':4,
        'CSC3206':7,'PRJ3213':7,'PRJ3223':8,'NET3204':8,'SEG3203':9,
    },
    '202304-direct': {
        'ENG1044':2,'CSC1202':2,'MTH1114':2,'CSC1024':2,
        'PRG1203':3,'SEG1201':3,'WEB1201':3,'OSS1014':3,
        'NET1014':6,  # shifted due to direct entry exemption
        'CSC2014':5,'CSC2103':4,'PRG2104':4,'ENG2042(MU22812)':4,
        'CSC3024':5,'NET2201':5,
        'CSC3206':7,'PRJ3213':7,'PRJ3223':8,'NET3204':8,'SEG3203':9,
    },
    '202309-normal': {
        'ENG1044':1,'CSC1202':1,'MTH1114':1,'CSC1024':1,
        'NET1014':2,
        'PRG1203':3,'SEG1201':3,'WEB1201':3,'OSS1014':3,
        'CSC2103':9,'CSC2014':6,'PRG2104':6,'ENG2044':6,'CSC3206':6,
        'PRJ3213':7,'CSC3024':7,'NET3204':7,'SEG3203':8,'PRJ3223':9,
    },
    '202309-precalc': {
        'MAT1013':1,'ENG1044':1,'CSC1202':1,'CSC1024':1,'WEB1201':1,
        'NET1014':2,
        'MTH1114':3,'PRG1203':3,'SEG1201':3,'OSS1014':3,
        'CSC2103':9,'CSC2014':6,'PRG2104':6,'ENG2044':6,'CSC3206':6,
        'PRJ3213':7,'CSC3024':7,'NET3204':7,'SEG3203':8,'PRJ3223':9,
    },
}

# Placeholder distribution per variant (counts) approximated from Scala listing
PLACEHOLDER_COUNTS: Dict[str, Dict[str,int]] = {
    '202301-normal': {'D1Y2':1,'D2Y2':1,'D4Y3':1,'D5Y3':1,'*F1':1,'*F2':1,'*F3':1},
    '202301-precalc': {'D1Y2':1,'D2Y2':1,'D4Y3':1,'D5Y3':1,'*F1':1,'*F2':1,'*F3':1},
    '202301-direct': {'D1Y2':1,'D2Y2':1,'D4Y3':1,'D5Y3':1,'*F1':1,'*F2':1,'*F3':1},
    '202304-normal': {'D1Y2':1,'D2Y2':1,'D4Y3':1,'D5Y3':1,'*F1':1,'*F2':1,'*F3':1},
    '202304-precalc': {'D1Y2':1,'D2Y2':1,'D4Y3':1,'D5Y3':1,'*F1':1,'*F2':1,'*F3':1},
    '202304-direct': {'D1Y2':1,'D2Y2':1,'D4Y3':1,'D5Y3':1,'*F1':1,'*F2':1,'*F3':1},
    '202309-normal': {'D1Y2':1,'D2Y2':1,'D4Y3':1,'D5Y3':1,'*F1':1,'*F2':1,'*F3':1},
    '202309-precalc': {'D1Y2':1,'D2Y2':1,'D4Y3':1,'D5Y3':1,'*F1':1,'*F2':1,'*F3':1},
}

# Communication skills code variant difference ENG2042(MU22812) vs ENG2044 handled by mapping above.

CATEGORY_OVERRIDES = {
    'PRJ3213':'capstone',
    'PRJ3223':'capstone',
    'SEG3203':'internship',
    'BIS2212(MU32422)':'compulsory',
    'ENG2042(MU22812)':'compulsory',
    'ENG2044':'compulsory',
    'MU42422':'compulsory',
    'MPU2012':'compulsory',
    'MPU3422':'compulsory',
    'MPU3332':'compulsory',
}

# Either pairs appear only when those MPU codes are present in the variant semesters (some direct variants later).

def build_variant(key: str) -> ProgrammeVariant:
    intake, entry_type, is_precalc = key.split('-')[0], key.split('-')[1], ('precalc' in key)
    variant = ProgrammeVariant(programme_code='BCS', intake_code=key.split('-')[0], entry_type=entry_type)

    semester_plans: Dict[int, SemesterPlan] = {}
    sem_map = SEM_MAPPING.get(key, {})
    for code, sem in sem_map.items():
        name, credit = COMMON_COURSES[code]
        category = CATEGORY_OVERRIDES.get(code, 'core')
        course = c(code, name, credit, sem, category)
        semester_plans.setdefault(sem, SemesterPlan(semester_number=sem)).required_courses.append(course)

    # Add either subject pairs where they logically appear (semester depending on mapping from Scala)
    # We approximate by placing them in earliest semester where other MPU codes appear or defined in Scala snippet.
    if 'normal' in key or 'precalc' in key:
        # Determine typical semester for pair: 1 or 2 or 3 depending on intake pattern
        if key.startswith('202301'):
            pair_sem = 1 if 'precalc' not in key else 1
        elif key.startswith('202304'):
            pair_sem = 3 if 'normal' in key else 3
        elif key.startswith('202309'):
            pair_sem = 2
        else:
            pair_sem = 1
        for pair in EITHER_PAIRS:
            # Represent as placeholder courses for progress tracking (not double counted in credits)
            semester_plans.setdefault(pair_sem, SemesterPlan(semester_number=pair_sem))
        variant.choice_pairs = [ChoicePair(option_codes=p) for p in EITHER_PAIRS]

    # Placeholder elective slots (we add placeholder courses so credits appear; adjust if real electives chosen)
    placeholder_counts = PLACEHOLDER_COUNTS.get(key, {})
    for ph_code, count in placeholder_counts.items():
        # assume each free elective is 4 credits, discipline elective 4 credits
        credit = 4
        category = 'elective-free' if ph_code.startswith('*F') else 'elective-discipline'
        for i in range(count):
            # approximate semester allocation: spread after semester 3
            allocate_sem = max(4, min(9, 3 + i + 1))
            name = PLACEHOLDER_NAMES.get(ph_code, ph_code)
            semester_plans.setdefault(allocate_sem, SemesterPlan(semester_number=allocate_sem)).required_courses.append(
                c(ph_code, name, credit, allocate_sem, category, placeholder=True)
            )
        if ph_code.startswith('*F'):
            variant.free_elective_placeholders.append(ph_code)
        else:
            variant.discipline_elective_placeholders.append(ph_code)

    # Sort semesters
    variant.semesters = [semester_plans[s] for s in sorted(semester_plans.keys())]
    
    # Populate elective groups from intake-specific store
    variant.elective_groups = build_elective_groups(intake)
    
    return variant


def load_bcs_variants() -> Dict[str, ProgrammeVariant]:
    variants: Dict[str, ProgrammeVariant] = {}
    for intake, entry_type, precalc_flag in VARIANT_SPECS:
        key = f"{intake}-{entry_type if not precalc_flag else 'precalc'}"
        variants[key] = build_variant(key)
    return variants

if __name__ == '__main__':
    variants = load_bcs_variants()
    for k,v in variants.items():
        progress = v.compute_progress(set())
        print(k, 'total credits:', progress.total_credits, 'semesters:', len(v.semesters))
