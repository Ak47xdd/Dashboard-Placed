"""
This module defines mappings for college and department name variants to their canonical forms.
"""


# Unified canonical mapping used by filters + charts
# wrong/spelling-variant(lowercase) -> canonical college name(Display name)
COLLEGE_VARIANT_CANONICAL_MAP = {
    "christ collage": "Christ College Vizhinjam",
    "christ college": "Christ College Vizhinjam",
    "amrita": "Amrita Vishwa Vidyapeetham Mysore",
    "amrita vishwa vidyapeetham mysuru": "Amrita Vishwa Vidyapeetham Mysore",
    "amrita vishwa vidyapeetham": "Amrita Vishwa Vidyapeetham Mysore",
    "government college for women": "Government College For Women, Thiruvananthapuram",
}

# wrong/spelling-variant(lowercase) -> canonical department name(Display name)
DEPARTMENT_VARIANT_CANONICAL_MAP = {
    # Add department typo/name variants here
    "integrated mca": "BCA + MCA",
    "computer applications": "BCA",
    "bcom finance": "BCom",
    "ba english": "BA English",
}