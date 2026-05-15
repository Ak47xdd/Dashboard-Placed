"""Maps instructional-fit questionnaire values to numeric profile scale.

Scale:
1 = High
2 = Medium
3 = Low
4 = None

Used for normalizing STUDENT_DATA columns instruct_Q2 and instruct_Q3
based on the options in Resources/Profiling questionnaire.docx.
"""

INSTRUCT_Q2_MAP = {
    "High": 1,
    "Medium": 2,
    "Low": 3,
    "None": 4,
}

INSTRUCT_Q3_MAP = {
    "High": 1,
    "Medium": 2,
    "Low": 3,
    "None": 4,
}

def normalize_instruct_value(x):
    """Normalize a single raw value to the 1..4 scale.

    Accepts already-numeric strings ("1".."4") as well as the option labels.
    Returns None if value is missing/unrecognized.
    """
    if x is None:
        return None
    s = str(x).strip()
    if s == "":
        return None

    # If already numeric scale
    # Note: CSV may contain values like "Low"/"High" or numeric codes.
    if s in {"1", "2", "3", "4"}:
        return int(s)

    # Sometimes values may come in as numeric in float-like format ("1.0")
    try:
        if float(s).is_integer() and str(int(float(s))) in {"1", "2", "3", "4"}:
            return int(float(s))
    except Exception:
        pass

    # Match option labels (case-insensitive)
    for k, v in INSTRUCT_Q2_MAP.items():
        if s.lower() == k.lower():
            return v

    return None

