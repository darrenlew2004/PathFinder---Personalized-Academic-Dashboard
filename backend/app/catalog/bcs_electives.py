"""
BCS Programme Electives extracted from BCSProgrammeElectives.scala
Maps elective group codes to available course options by year/intake stores
"""
from typing import Dict, List

try:
    from .program_catalog_models import ElectiveGroup, Course
except ImportError:
    from program_catalog_models import ElectiveGroup, Course

# Year 2 elective definitions by store version
ELECTIVES_Y2_2019 = {
    'D1Y2': [
        ('PRG2214', 'FunctionalProgrammingPrinciples', 4),
        ('NET2102', 'DataCommunications', 4),
        ('BIS2216', 'DataMiningandKnowledgeDiscoveryFundamentals', 4),
    ],
    'D2Y2': [
        ('CSC2044', 'ConcurrentProgramming', 4),
        ('SEG2102', 'DatabaseManagementSystems', 4),
        ('IST2134', 'SocialMediaAnalytics', 4),
    ],
}

ELECTIVES_Y3_2019 = {
    'D4Y3': [
        ('CSC3044', 'ComputerSecurity', 4),
        ('CSC3014', 'ComputerVision', 4),
        ('PRG3014', 'UI/UXDesignandDevelopment', 4),
        ('CSC3209', 'SoftwareArchitectureandDesignPatterns', 4),
    ],
    'D5Y3': [
        ('CSC3034', 'ComputationalIntelligence', 4),
        ('CSC3064', 'DatabaseEngineering', 4),
        ('PRG2205', 'ProgrammingLanguages', 4),
    ],
}

ELECTIVES_Y2_2021 = {
    'D1Y2': [
        ('PRG2214', 'FunctionalProgrammingPrinciples', 4),
        ('NET2102', 'DataCommunications', 4),
        ('BIS2216', 'DataMiningandKnowledgeDiscoveryFundamentals', 4),
        ('IST2334', 'WebandNetworkAnalytics', 4),
    ],
    'D2Y2': [
        ('CSC2044', 'ConcurrentProgramming', 4),
        ('SEG2102', 'DatabaseManagementSystems', 4),
        ('BIS2216', 'DataMiningandKnowledgeDiscoveryFundamentals', 4),
    ],
}

ELECTIVES_Y3_2021 = {
    'D4Y3': [
        ('CSC3044', 'ComputerSecurity', 4),
        ('CSC3014', 'ComputerVision', 4),
        ('PRG3014', 'UI/UXDesignandDevelopment', 4),
        ('CSC3209', 'SoftwareArchitectureandDesignPatterns', 4),
    ],
    'D5Y3': [
        ('CSC3034', 'ComputationalIntelligence', 4),
        ('CSC3064', 'DatabaseEngineering', 4),
        ('PRG2205', 'ProgrammingLanguages', 4),
    ],
}

ELECTIVES_Y2_2022 = {
    'D1Y2': [
        ('PRG2214', 'FunctionalProgrammingPrinciples', 4),
        ('NET2102', 'DataCommunications', 4),
        ('SEG2102', 'DatabaseManagementSystems', 4),
        ('IST2334', 'WebandNetworkAnalytics', 4),
        ('SWA2124', 'SocialandWebAnalytics', 4),
    ],
    'D2Y2': [
        ('CSC2044', 'ConcurrentProgramming', 4),
        ('SEG2102', 'DatabaseManagementSystems', 4),
        ('BIS2216', 'DataMiningandKnowledgeDiscoveryFundamentals', 4),
    ],
}

ELECTIVES_Y3_2022 = {
    'D4Y3': [
        ('CSC3044', 'ComputerSecurity', 4),
        ('CSC3014', 'ComputerVision', 4),
        ('PRG3014', 'UI/UXDesignandDevelopment', 4),
        ('CSC3209', 'SoftwareArchitectureandDesignPatterns', 4),
    ],
    'D5Y3': [
        ('CSC3034', 'ComputationalIntelligence', 4),
        ('CSC3064', 'DatabaseEngineering', 4),
        ('PRG2205', 'ProgrammingLanguages', 4),
    ],
}

ELECTIVES_Y2_2023 = {
    'D1Y2': [
        ('PRG2214', 'FunctionalProgrammingPrinciples', 4),
        ('NET2102', 'DataCommunications', 4),
        ('PRG2205', 'ProgrammingLanguages', 4),
        ('SEG2102', 'DatabaseManagementSystems', 4),
        ('NET2201', 'ComputerNetworks', 4),
    ],
    'D2Y2': [
        ('CSC2044', 'ConcurrentProgramming', 4),
        ('SEG2102', 'DatabaseManagementSystems', 4),
        ('BIS2216', 'DataMiningandKnowledgeDiscoveryFundamentals', 4),
        ('SWA2124', 'SocialandWebAnalytics', 4),
    ],
}

ELECTIVES_Y3_2023 = {
    'D4Y3': [
        ('CSC3044', 'ComputerSecurity', 4),
        ('CSC3014', 'ComputerVision', 4),
        ('CSC3209', 'SoftwareArchitectureandDesignPatterns', 4),
    ],
    'D5Y3': [
        ('CSC3034', 'ComputationalIntelligence', 4),
        ('CSC3064', 'DatabaseEngineering', 4),
        ('PRG3014', 'UI/UXDesignandDevelopment', 4),
    ],
}

ELECTIVES_Y2_2024 = {
    'D1Y2': [
        ('CSC2014', 'DigitalImageProcessing', 4),
        ('SWA2124', 'SocialandWebAnalytics', 4),
        ('BIS2102', 'InformationSystemAnalysis&Design', 4),
    ],
    'D2Y2': [
        ('PRG2214', 'FunctionalProgrammingPrinciples', 4),
        ('NET2102', 'DataCommunications', 4),
        ('PRG2205', 'ProgrammingLanguages', 4),
        ('SEG2102', 'DatabaseManagementSystems', 4),
    ],
    'D3Y2': [
        ('CSC2044', 'ConcurrentProgramming', 4),
        ('BIS2216', 'DataMiningandKnowledgeDiscoveryFundamentals', 4),
        ('NET2201', 'ComputerNetworks', 4),
        ('CSC2074', 'MobileApplicationDevelopment', 4),
    ],
}

ELECTIVES_Y3_2024 = {
    'D4Y3': [
        ('CSC3044', 'ComputerSecurity', 4),
        ('CSC3014', 'ComputerVision', 4),
        ('CSC3209', 'SoftwareArchitectureandDesignPatterns', 4),
    ],
    'D5Y3': [
        ('CSC3034', 'ComputationalIntelligence', 4),
        ('CSC3064', 'DatabaseEngineering', 4),
        ('PRG3014', 'UI/UXDesignandDevelopment', 4),
        ('CSC3074', 'Cloud Computing', 4),
    ],
}

ELECTIVES_Y2_2025 = {
    'D1Y2': [
        ('CSC2014', 'DigitalImageProcessing', 4),
        ('SWA2124', 'SocialandWebAnalytics', 4),
        ('BIS2102', 'InformationSystemAnalysis&Design', 4),
    ],
    'D2Y2': [
        ('PRG2214', 'FunctionalProgrammingPrinciples', 4),
        ('NET2102', 'DataCommunications', 4),
        ('PRG2205', 'ProgrammingLanguages', 4),
        ('SEG2102', 'DatabaseManagementSystems', 4),
        ('NET3054', 'IoTNetworkingandSecurity', 4),
    ],
    'D3Y2': [
        ('CSC2044', 'ConcurrentProgramming', 4),
        ('BIS2216', 'DataMiningandKnowledgeDiscoveryFundamentals', 4),
        ('NET2201', 'ComputerNetworks', 4),
        ('CSC2074', 'MobileApplicationDevelopment', 4),
    ],
}

ELECTIVES_Y3_2025 = {
    'D4Y3': [
        ('CSC3044', 'ComputerSecurity', 4),
        ('CSC3014', 'ComputerVision', 4),
        ('CSC3209', 'SoftwareArchitectureandDesignPatterns', 4),
    ],
    'D5Y3': [
        ('CSC3034', 'ComputationalIntelligence', 4),
        ('CSC3064', 'DatabaseEngineering', 4),
        ('PRG3014', 'UI/UXDesignandDevelopment', 4),
        ('CSC3074', 'Cloud Computing', 4),
    ],
}

# Map intake codes to store version
INTAKE_TO_STORE: Dict[str, tuple] = {
    '202301': (ELECTIVES_Y2_2023, ELECTIVES_Y3_2023),
    '202304': (ELECTIVES_Y2_2023, ELECTIVES_Y3_2023),
    '202309': (ELECTIVES_Y2_2023, ELECTIVES_Y3_2023),
    '202401': (ELECTIVES_Y2_2024, ELECTIVES_Y3_2024),
    '202404': (ELECTIVES_Y2_2024, ELECTIVES_Y3_2024),
    '202409': (ELECTIVES_Y2_2024, ELECTIVES_Y3_2024),
    '202501': (ELECTIVES_Y2_2025, ELECTIVES_Y3_2025),
}


def build_elective_groups(intake_code: str) -> Dict[str, ElectiveGroup]:
    """Build ElectiveGroup objects for a specific intake"""
    stores = INTAKE_TO_STORE.get(intake_code, (ELECTIVES_Y2_2023, ELECTIVES_Y3_2023))
    y2_store, y3_store = stores
    
    groups: Dict[str, ElectiveGroup] = {}
    
    for group_code, courses_data in y2_store.items():
        options = [
            Course(
                subject_code=code,
                subject_name=name,
                credit=credit,
                category='elective-discipline',
                elective_group=group_code
            )
            for code, name, credit in courses_data
        ]
        groups[group_code] = ElectiveGroup(group_code=group_code, year_level=2, options=options)
    
    for group_code, courses_data in y3_store.items():
        options = [
            Course(
                subject_code=code,
                subject_name=name,
                credit=credit,
                category='elective-discipline',
                elective_group=group_code
            )
            for code, name, credit in courses_data
        ]
        groups[group_code] = ElectiveGroup(group_code=group_code, year_level=3, options=options)
    
    return groups


if __name__ == '__main__':
    # Test loading
    import sys, pathlib
    ROOT = pathlib.Path(__file__).resolve().parents[3]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from backend.app.catalog.program_catalog_models import ElectiveGroup, Course
    
    groups = build_elective_groups('202301')
    for code, group in groups.items():
        print(f"{code} (Year {group.year_level}): {len(group.options)} options")
        for opt in group.options:
            print(f"  - {opt.subject_code}: {opt.subject_name}")
