from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import os
from datetime import datetime, timezone
from google.oauth2 import service_account
import gspread

app = FastAPI(title="Profiling Form API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SHEET_NAME = "STUDENTS_DATA"
WORKSHEET_INDEX = 0

def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = service_account.Credentials.from_service_account_file("./service_key.json", scopes=scopes)
    return gspread.authorize(creds)

@app.post("/form/submit-profile")
async def submit_profile(form_data: dict):
    csv_path = '../data/STUDENTS - Sheet1.csv'
    
    df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame()
    student_id = len(df) + 1
    created_at = datetime.now(timezone.utc).isoformat()
    
    data = {
        'student_id': student_id,
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
    for i in range(1,6):
        data[f'behave_Q{i}'] = str(s3.get(f'behave_Q{i}', ''))
    
    s4 = form_data.get('section4', {})
    for i in range(1,5):
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
    
    new_df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    new_df.to_csv(csv_path, index=False)
    
    # FASTAPI GSPREAD WITH DRIVE SCOPE - FIXED 403
    try:
        client = get_gsheet_client()
        sheet = client.open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)
        sheet.clear()
        values = [new_df.columns.tolist()] + new_df.fillna('').values.tolist()
        sheet.update(values=values)
        print(f"Synced #{student_id}")
    except Exception as e:
        print(f"Sheet sync: {e}")
    
    return {"student_id": student_id, "message": "SUCCESS CSV + Sheet"}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

