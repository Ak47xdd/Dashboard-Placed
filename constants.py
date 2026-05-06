# All application constants should be defined here


REFRESH_SECONDS = 30

# Toggle data source:
# - USE_CSV = True  => read from local CSV files
# - USE_CSV = False => read from Supabase
USE_CSV = False

MAIN_CSV = "STUDENTS - Sheet1"
CSV_FILE = "CLASSIFICATIONS - Sheet1 (1).csv"

# ---- Supabase connection ----
SUPABASE_URL = "https://bzvztzxrrziqrfokcyuf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ6dnp0enhycnppcXJmb2tjeXVmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzk5MzMyNCwiZXhwIjoyMDkzNTY5MzI0fQ.HAUOI6sm4EOLKcKPScbkeA7fkt6Vtx0Iq2hdzRiXfaY"

# Table schema provided by you: public."CLASSIFICATION"
SUPA_DB = "CLASSIFICATION"

