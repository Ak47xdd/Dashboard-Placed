"""
Submit the student questionnaire data into Supabase database STUDENT_DATA.
"""
 
import requests
import schema
import os
from dotenv import load_dotenv  
load_dotenv()
 
MAIN_TABLE_NAME = "STUDENT_DATA"
CLASS_TABLE_NAME = "CLASSIFICATION"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
 
student_res = None
student_res_json = None
 
def submit_student_data(form_data: dict):
    """
    Insert the submitted questionnaire directly into Supabase.
    """
    
    global student_res, student_res_json
 
    data = schema.schema(form_data)
 
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
 
    student_endpoint = f"{SUPABASE_URL}/rest/v1/{MAIN_TABLE_NAME}"
    student_res = requests.post(student_endpoint, headers=headers, json=data)
 
    if student_res.text:
        try:
            student_res_json = student_res.json()
        except Exception:
            student_res_json = None
    else:
        student_res_json = None
 
    if student_res.status_code not in (200, 201):
        print("[submit-profile] ERROR inserting student:", student_res.status_code, student_res.text)
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
 
    return student_res_json