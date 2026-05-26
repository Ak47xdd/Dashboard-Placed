"""
Maps instructional-fit questionnaire values to numeric profile scale.

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

    # If already numeric, map questionnaire scale (3=Low, 2=Medium, 1=High, 4=None)
    # to the output profile scale (1 High, 2 Medium, 3 Low, 4 None).
    # In the dataset, instruct_Q* are stored as the questionnaire numeric options.
    # So: 1->1, 2->2, 3->3, 4->4 is identity, BUT here UI expects
    # the labels (High/Medium/Low/None) not the raw option number.
    # normalize_instruct_value therefore intentionally keeps the same mapping.
    if s in {"1", "2", "3", "4"}:
        return int(s)

    try:
        if float(s).is_integer() and str(int(float(s))) in {"1", "2", "3", "4"}:
            return int(float(s))
    except Exception:
        pass

    for k, v in INSTRUCT_Q2_MAP.items():
        if s.lower() == k.lower():
            return v

    return None

