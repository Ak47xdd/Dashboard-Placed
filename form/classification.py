"""
Submit the calculated CLASSIFICATION data into Supabase after student data is inserted.
"""

import requests
import os
import pandas as _pd
import schema
import marking
import student_data

from dotenv import load_dotenv  
load_dotenv()

MAIN_TABLE_NAME = "STUDENT_DATA"
CLASS_TABLE_NAME = "CLASSIFICATION"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def submit_classification_data(classification_payload: dict):
    """
    Insert the calculated classification data into Supabase.
    """
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }

    data = schema.schema(classification_payload)
    inserted = student_data.student_res_json if student_data.student_res_json is not None else (student_data.student_res.text or [])

    inserted = student_data.student_res.json() if student_data.student_res.text else []
    # Supabase returns inserted rows when Prefer: return=representation is set.
    inserted_row = None
    if isinstance(inserted, list) and inserted:
        inserted_row = inserted[0]
    elif isinstance(inserted, dict):
        inserted_row = inserted
    
    student_id = None
    if inserted_row:
        student_id = inserted_row.get('student_id') or inserted_row.get('id') or inserted_row.get('Student_ID')
    
    row_series = _pd.Series(dict(data))
    if student_id is not None:
        row_series["student_id"] = student_id
        
        classified_series = marking.calculate_scores(row_series)
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