from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import requests
from marking import generate_classifications
from datetime import datetime, timezone
import os
from dotenv import load_dotenv  
load_dotenv()

app = FastAPI(
    title="Profiling Form API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    )

app.add_middleware(
    CORSMiddleware,
    # Allow local development + Render deployments.
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://dashboard-app-zggs.onrender.com",
        "https://dashboard-app-zggs.onrender.com/submit-profile",
        "https://form-placed.vercel.app",
        "https://form-placed.vercel.app/profiling.html",
        "https://cron-job.org",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MAIN_TABLE_NAME = "STUDENT_DATA"
CLASS_TABLE_NAME = "CLASSIFICATION"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def sync_STUDENT_csv_to_supabase():
    df = pd.read_csv('./data/STUDENTS - Sheet1.csv')
    print("Synced STUDENT_DATA CSV to Supabase table")

    records = df.to_dict(orient='records')

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates" # Standard PostgREST upsert behavior
    }
    
    endpoint = f"{SUPABASE_URL}/rest/v1/{MAIN_TABLE_NAME}"
    res = requests.post(endpoint, headers=headers, json=records)

    if res.status_code in [200, 201]:
        print("Successfully synced STUDENT data!")
    else:
        print(f"Error: {res.status_code} - {res.text}")
        
def sync_CLASS_csv_to_supabase():
    df = pd.read_csv('./data/CLASSIFICATIONS - Sheet1 (1).csv')
    print("Synced CLASSIFICATION CSV to Supabase table")

    records = df.to_dict(orient='records')

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates" # Standard PostgREST upsert behavior
    }
    
    endpoint = f"{SUPABASE_URL}/rest/v1/{CLASS_TABLE_NAME}"
    res = requests.post(endpoint, headers=headers, json=records)

    if res.status_code in [200, 201]:
        print("Successfully synced CLASSIFICATION data!")
    else:
        print(f"Error: {res.status_code} - {res.text}")
        
@app.get("/cron-task")
def cron_job():
    return {"Cron job complete, next one in 10 minutes"}

@app.post("/form/submit-profile")
def submit_profile(form_data: dict):
    """Insert the submitted questionnaire directly into Supabase.

    This removes the previous CSV-first behavior.
    """
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

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }

    # Insert into STUDENT_DATA (MAIN_TABLE_NAME)
    student_endpoint = f"{SUPABASE_URL}/rest/v1/{MAIN_TABLE_NAME}"

    # Debug: what backend actually receives
    print("[submit-profile] received form_data keys:", list(form_data.keys()))
    print("[submit-profile] student insert payload keys:", sorted(list(data.keys())))
    
    student_res = requests.post(student_endpoint, headers=headers, json=data)

    # Always surface Supabase response for debugging.
    if student_res.text:
        try:
            student_res_json = student_res.json()
        except Exception:
            student_res_json = None
    else:
        student_res_json = None

    # If Supabase rejected the write, we will get a non-2xx status.
    if student_res.status_code not in (200, 201):
        return {
            "student_id": None,
            "message": f"ERROR inserting student: {student_res.status_code}",
            "supabase_response": student_res.text,
            "supabase_response_json": student_res_json,
            "student_insert_payload": data,
        }

    if student_res_json is not None:
        print("[submit-profile] student_res_json:", student_res_json)
    else:
        print("[submit-profile] student_res_text:", student_res.text)

    inserted = student_res_json if student_res_json is not None else (student_res.text or [])

    inserted = student_res.json() if student_res.text else []
    # Supabase returns inserted rows when Prefer: return=representation is set.
    inserted_row = None
    if isinstance(inserted, list) and inserted:
        inserted_row = inserted[0]
    elif isinstance(inserted, dict):
        inserted_row = inserted

    # Some schemas may return `id` instead of `student_id`.
    student_id = None
    if inserted_row:
        student_id = inserted_row.get('student_id') or inserted_row.get('id') or inserted_row.get('Student_ID')

    from marking import calculate_scores  
    import pandas as _pd

    row_series = _pd.Series(dict(data))
    if student_id is not None:
        row_series["student_id"] = student_id

    classified_series = calculate_scores(row_series)
    classification_payload = (
        classified_series.to_dict()
        if hasattr(classified_series, "to_dict")
        else dict(classified_series)
    )

    class_endpoint = f"{SUPABASE_URL}/rest/v1/{CLASS_TABLE_NAME}"
    class_res = requests.post(
        class_endpoint,
        headers={
            **headers,
            "Prefer": "resolution=merge-duplicates,return=representation",
        },
        json=classification_payload,
    )

    if class_res.status_code not in (200, 201):
        return {
            "student_id": student_id,
            "message": f"STUDENT inserted but classification failed: {class_res.status_code}",
            "supabase_class_response": class_res.text,
            "classification_payload": classification_payload,
        }

    latest_student = None
    latest_class = None

    try:
        latest_student_url = (
            f"{SUPABASE_URL}/rest/v1/{MAIN_TABLE_NAME}"
            f"?select=student_id&order=created_at.desc&limit=1"
        )
        latest_student_res = requests.get(
            latest_student_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Accept": "application/json",
            },
            timeout=30,
        )
        if latest_student_res.text:
            latest_student_res.raise_for_status()
            latest_student = latest_student_res.json()
    except Exception as e:
        print("[submit-profile] read-back student failed:", str(e))

    try:
        latest_class_url = (
            f"{SUPABASE_URL}/rest/v1/{CLASS_TABLE_NAME}"
            f"?select=student_id&order=created_at.desc&limit=1"
        )
        latest_class_res = requests.get(
            latest_class_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Accept": "application/json",
            },
            timeout=30,
        )
        if latest_class_res.text:
            latest_class_res.raise_for_status()
            latest_class = latest_class_res.json()
    except Exception as e:
        # Fallback: no order clause
        print("[submit-profile] read-back class ordered failed:", str(e))
        try:
            latest_class_url = (
                f"{SUPABASE_URL}/rest/v1/{CLASS_TABLE_NAME}"
                f"?select=student_id&limit=1"
            )
            latest_class_res = requests.get(
                latest_class_url,
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Accept": "application/json",
                },
                timeout=30,
            )
            if latest_class_res.text:
                latest_class_res.raise_for_status()
                latest_class = latest_class_res.json()
        except Exception as e2:
            print("[submit-profile] read-back class fallback failed:", str(e2))


    # Debug classification write success response
    print("[submit-profile] class_res.status_code:", class_res.status_code)
    if class_res.text:
        try:
            print("[submit-profile] class_res.json:", class_res.json())
        except Exception:
            print("[submit-profile] class_res.text:", class_res.text)

    return {
        "student_id": student_id,
        "message": "SUCCESS Supabase",
        "readback_latest_student": latest_student,
        "readback_latest_class": latest_class,
    }
    
if __name__ == "__main__":
    uvicorn.run("form:app", host="0.0.0.0", port=8001, reload=True)


