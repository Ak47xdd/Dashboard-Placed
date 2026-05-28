"""
Schema module responsible for transforming raw form data into the structured format
"""
 
 
from datetime import datetime, timezone
import os
import requests
from dotenv import load_dotenv  
load_dotenv()
 
MAIN_TABLE_NAME = "STUDENT_DATA"
CLASS_TABLE_NAME = "CLASSIFICATION"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
 
def schema(form_data: dict):
    created_at = datetime.now(timezone.utc).isoformat()
 
    # Build the STUDENT_DATA row.
    latest_id_url = (
        f"{SUPABASE_URL}/rest/v1/{MAIN_TABLE_NAME}"
        f"?select=student_id&order=student_id.desc&limit=1"
    )
    latest_id_res = requests.get(
        latest_id_url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Accept": "application/json",
        },
        timeout=30,
    )
    latest_student = latest_id_res.json() if latest_id_res.text else []
    latest_student_id = None
    if isinstance(latest_student, list) and latest_student:
        latest_student_id = latest_student[0].get("student_id")
 
    try:
        latest_student_id_int = int(latest_student_id) if latest_student_id not in (None, "") else 0
    except Exception:
        latest_student_id_int = 0
 
    global new_student_id
    new_student_id = latest_student_id_int + 1
    
    data = {
        'student_id': new_student_id,
        'created_at': created_at,
        'student_name': form_data.get('section0', {}).get('student_name', ''),
        'mobile_number': form_data.get('section0', {}).get('mobile_number', ''),
        'email_id': form_data.get('section0', {}).get('email_id', ''),
        'college_name': form_data.get('section0', {}).get('college_name', ''),
        'department': form_data.get('section0', {}).get('department', ''),
        'course_type': form_data.get('section1', {}).get('course_type', ''),
        'year': str(form_data.get('section1', {}).get('year', '')),
        'medium': form_data.get('section1', {}).get('medium', ''),
        'have_prep_test': form_data.get('section1', {}).get('have_prep_test', ''),
        'career_goal': form_data.get('section1', {}).get('career_goal', ''),
    }
 
    s2 = form_data.get('section2', {})
    for subj in ['quant_answers', 'logic_answers', 'verbal_answers']:
        answers = s2.get(subj, [])
        prefix = subj.split('_')[0]
        for i in range(5):
            data[f'{prefix}_Q{i+1}'] = str(answers[i]) if i < len(answers) else ''
 
    s3 = form_data.get('section3', {})
    for i in range(1, 6):
        data[f'behave_Q{i}'] = str(s3.get(f'behave_Q{i}', ''))
 
    s4 = form_data.get('section4', {})
    for i in range(1, 5):
        data[f'learn_Q{i}'] = str(s4.get(f'learn_Q{i}', ''))
 
    s5 = form_data.get('section5', {})
    data.update({
        'instruct_Q1': str(s5.get('instruct_Q1', '')),
        'instruct_Q2': str(s5.get('instruct_Q2', '')),
        'instruct_Q3': str(s5.get('instruct_Q3', '')),
        'instruct_Q4': str(s5.get('instruct_Q4', '')),
        'instruct_Q5': str(s5.get('instruct_Q5', '')),
        'instruct_Q6': str(s5.get('instruct_Q6', '')),
    })
 
    s5a = form_data.get('section5a', {})
    data['content_pref_Q1'] = str(s5a.get('content_pref_Q1', s5a.get('content_Q1', '')))
    data['content_pref_Q2'] = str(s5a.get('content_pref_Q2', s5a.get('content_Q2', '')))
    data['content_pref_Q3'] = str(s5a.get('content_pref_Q3', s5a.get('content_Q3', '')))
 
    s5b = form_data.get('section5b', {})
    data.update({
        'engage_Q1': str(s5b.get('engage_Q1', '')),
        'engage_Q2': str(s5b.get('engage_Q2', '')),
        'engage_Q3': str(s5b.get('engage_Q3', '')),
        'engage_Q4': str(s5b.get('engage_Q4', '')),
        'commit_Q1': str(s5b.get('commit_Q1', '')),
        'commit_Q2': str(s5b.get('commit_Q2', '')),
        'commit_Q3': str(s5b.get('commit_Q3', '')),
        'commit_Q4': str(s5b.get('commit_Q4', '')),
    })
    return data
 