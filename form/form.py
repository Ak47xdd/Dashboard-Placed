"""
Form submission API for the Profiling Form.
"""
 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import student_data
import classification
 
app = FastAPI(
    title="Profiling Form API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
 
ALLOWED_ORIGINS = [
    "https://form-placed.vercel.app",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://dashboard-app-zggs.onrender.com",
    "https://cron-job.org",
]
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "apikey"],
)
 
 
@app.options("/{full_path:path}")
async def global_options_handler(full_path: str, request: Request):
    """
    Catch-all OPTIONS handler. Ensures CORS preflight succeeds even when
    the Render instance is cold-starting — the middleware still injects the
    Access-Control-Allow-Origin header on this 200 response.
    """
    origin = request.headers.get("origin", "")
    if origin not in ALLOWED_ORIGINS:
        return JSONResponse(status_code=403, content={"detail": "Origin not allowed"})
    return JSONResponse(
        status_code=200,
        content={},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, apikey",
        },
    )
 
 
@app.get("/cron-task")
def cron_job():
    """
    Cron task — triggered every 10 minutes by cron-job.org to prevent
    the Render free-tier instance from spinning down.
    """
    return {"status": "ok", "message": "Cron job complete, next one in 10 minutes"}
 
 
@app.post("/form/submit-profile")
def submit_profile(form_data: dict):
    """
    Insert the submitted questionnaire into Supabase, then insert
    the calculated classification row.
    """
    student_result = student_data.submit_student_data(form_data)
 
    # If student insert failed, surface the error immediately.
    if isinstance(student_result, dict) and student_result.get("student_id") is None:
        return JSONResponse(status_code=500, content=student_result)
 
    class_result = classification.submit_classification_data(form_data)
 
    if isinstance(class_result, dict) and "failed" in class_result.get("message", ""):
        return JSONResponse(status_code=500, content=class_result)
 
    return JSONResponse(status_code=200, content=class_result or {"message": "SUCCESS"})
 
if __name__ == "__main__":
    uvicorn.run("form:app", host="0.0.0.0", port=8001, reload=True)