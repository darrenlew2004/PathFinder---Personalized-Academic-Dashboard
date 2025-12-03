import csv
import re 
import json

def parse_subject_string(subject_str):
    """
    Parse the subject string format and convert to proper JSON.
    The format is like: {courseworkPercentage=1, examMonth=12, ...}
    """
    # Replace = with : and wrap keys in quotes
    subject_str = re.sub(r'(\w+)=', r'"\1":', subject_str)
    
    # Handle values: wrap non-numeric values in quotes
    # Match pattern: "key": value (where value is not a number and not already quoted)
    def quote_value(match):
        key = match.group(1)
        value = match.group(2).strip()
        
        # If value is empty or just whitespace
        if not value or value == '':
            return f'"{key}":""'
        # If value is already a number
        if value.replace('.', '', 1).isdigit():
            return f'"{key}":{value}'
        # If value is already quoted
        if value.startswith('"'):
            return f'"{key}":{value}'
        # Otherwise quote it
        return f'"{key}":"{value}"'
    
    # Handle the pattern "key": value, or "key": value}
    subject_str = re.sub(r'"(\w+)":\s*([^,}\s][^,}]*?)(?=[,}])', quote_value, subject_str)
    
    # Handle empty values (": ,") -> ("":"",)
    subject_str = re.sub(r':\s*,', r':"",', subject_str)
    subject_str = re.sub(r':\s*}', r':""}', subject_str)
    
    try:
        return json.loads(subject_str)
    except json.JSONDecodeError as e:
        # Silent failure - just return None
        return None

def flatten_student_data(input_file, output_file):
    """
    Flatten student data so each row represents one subject.
    """
    flattened_rows = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row in reader:
            if len(row) < 2:
                continue
                
            student_id = row[0]
            subjects_str = row[1]
            
            # Skip empty subject lists
            if subjects_str == '[]':
                continue
            
            # Remove outer brackets
            subjects_str = subjects_str.strip('[]')
            
            # Split by '}, {' to separate subjects
            subject_parts = re.split(r'\},\s*\{', subjects_str)
            
            for subject_part in subject_parts:
                # Add back the braces
                if not subject_part.startswith('{'):
                    subject_part = '{' + subject_part
                if not subject_part.endswith('}'):
                    subject_part = subject_part + '}'
                
                # Parse the subject data
                subject_data = parse_subject_string(subject_part)
                
                if subject_data:
                    flattened_row = {
                        'student_id': student_id,
                        'subject_code': subject_data.get('subjectCode', ''),
                        'subject_name': subject_data.get('subjectName', ''),
                        'coursework_percentage': subject_data.get('courseworkPercentage', ''),
                        'exam_percentage': subject_data.get('examPercentage', ''),
                        'overall_percentage': subject_data.get('overallPercentage', ''),
                        'grade': subject_data.get('grade', ''),
                        'exam_month': subject_data.get('examMonth', ''),
                        'exam_year': subject_data.get('examYear', ''),
                        'status': subject_data.get('status', '')
                    }
                    flattened_rows.append(flattened_row)
    
    # Write to output CSV
    if flattened_rows:
        fieldnames = ['student_id', 'subject_code', 'subject_name', 
                     'coursework_percentage', 'exam_percentage', 'overall_percentage',
                     'grade', 'exam_month', 'exam_year', 'status']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_rows)
        
        print(f"Successfully flattened {len(flattened_rows)} subject records")
        print(f"Output written to: {output_file}")
    else:
        print("No data to write")

if __name__ == '__main__':
    input_file = 'data/subjectplanning_students.csv'
    output_file = 'data/flattened_students_subjects.csv'
    
    flatten_student_data(input_file, output_file)
