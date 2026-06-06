"""
This module defines all constants used across the application, including configuration settings,
"""

# All application constants should be defined here

REFRESH_SECONDS = 30

# Toggle data source:
# - USE_CSV = True  => read from local CSV files (TEST, STATIC DATA)
# - USE_CSV = False => read from Supabase (LIVE DATABASE)
USE_CSV = False

MAIN_CSV = "STUDENTS - Sheet1"
CSV_FILE = "CLASSIFICATIONS - Sheet1 (1).csv"

# Table schema provided by supabase: public."CLASSIFICATION" & public."STUDENT_DATA"
SUPA_DB = "CLASSIFICATION"
SUPA_RAW_DB = "STUDENT_DATA"
