# Dashboard-Placed

A Streamlit-based analytics dashboard for student placement and learning-questionnaire insights. The app supports two views:

- **Response Dashboard** (aggregated / classification-style insights)
- **Student Evaluation Dashboard** (student-level questionnaire responses with rich charts + filtering)

It provides interactive visualizations, KPI cards, searchable tables, and periodic auto-refresh.

![Streamlit Version](https://img.shields.io/badge/Streamlit-1.57.0+-06B3C9?style=flat&logo=streamlit)
![Python Version](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python)

---

## Features

- **Two Data Views**
  - Response Dashboard
  - Student Evaluation Dashboard
- **Interactive Filters (Student Evaluation view)**
  - Filter by **College**, **Department**, and **Year**
  - Support for **custom filter text** (exact/custom matching)
  - **Clear All Filters** button
- **Normalization for Consistent Categories**
  - College/Department spelling variants are normalized using canonical maps.
- **Rich Visualizations (Student Evaluation view)**
  - Sunburst (College → Department → Year)
  - Pie charts (e.g., medium, career goal)
  - Grouped bar charts (career goals vs prep-test)
  - Stacked bar (learning seek-answer profile)
  - Bubble chart (teaching style fit)
  - Donuts (content vs engagement)
  - Score analytics charts (when score columns exist)
- **KPIs (Student Evaluation view)**
  - Total Students
  - Colleges / Departments counts
  - In-Campus Placement Seekers (% derived from `career_goal`)
- **Student Table + Export**
  - Student responses table with column cleanup
  - Student ID selection filter
  - **Export CSV** (filtered dataset)
- **Auto-Refresh**
  - Automatic refresh every `REFRESH_SECONDS` (default: 30s)
  - Manual **Refresh** button that busts Streamlit caches
- **Custom Styling**
  - Background and UI enhancements via `frontend/`

---

## Tech Stack

| Category        | Technology                                                 |
| --------------- | ---------------------------------------------------------- |
| Frontend        | [Streamlit](https://streamlit.io/)                         |
| Data Processing | [Pandas](https://pandas.pydata.org/)                       |
| Visualizations  | [Plotly](https://plotly.com/python/)                       |
| Data Source     | Supabase (default) / Local CSV (optional)                  |
| API Integration | Supabase REST (no external supabase SDK)                   |
| Authentication  | Supabase JWT via env vars (`SUPABASE_URL`, `SUPABASE_KEY`) |

---

## Project Structure

```
Dashboard-Placed/
├── app.py
├── constants.py
├── filter.py
├── student_dashboard.py
├── db_queries.py
├── supabase_client.py
├── college_dept_map.py
├── questionnaire_instruct_map.py
├── wake.py
├── requirements.txt
├── deployment.yaml
├── Dockerfile
├── .dockerignore
├── .gitignore
├── convert_logo_to_base64.py
├── data/
│   ├── __init__.py
│   └── data.py
├── data/backups/
│   ├── BACKUPS.md
│   ├── CLASSIFICATION.csv
│   └── STUDENT_DATA.csv
├── frontend/
│   ├── __init__.py
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── nginx.conf
│   ├── bg.py
│   ├── bg.css
│   ├── dashboard.css
│   ├── dashboard.html
│   ├── filter_styles.css
│   ├── index.html
│   ├── dashboard.css
│   ├── profiling.css
│   ├── profiling.html
│   ├── profiling.js
│   ├── script.js
│   ├── styles.css
│   ├── styles.py
│   ├── template.html
│   └── countdown.html
├── form/
│   ├── __init__.py
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── form.py
│   ├── schema.py
│   ├── sync.py
│   ├── backup.py
│   ├── student_data.py
│   ├── classification.py
│   ├── marking.py
│   └── requirements.txt
├── Resources/
│   ├── Placed.jpg
│   ├── Placed_base64.txt
│   └── LOGO.png
│   └── Profiling questionnaire.docx
└── README.md
```

## Containerization & Deployment (Docker + Kubernetes)

The repo includes Dockerfiles for the main Streamlit app and for the `frontend/` and `form/` services, plus a Kubernetes manifest for deployment.

### Docker (local)

From the repository root:

- Main Streamlit container:
  - `Dockerfile`
- Nginx/static frontend container:
  - `frontend/Dockerfile`
- Form/collection container:
  - `form/Dockerfile`

Example build commands (adjust image names as needed):

```bash
docker build -t dashboard-placed:latest .
docker build -t dashboard-placed-frontend:latest ./frontend
docker build -t dashboard-placed-form:latest .
```

### Kubernetes (pods + deployment)

- Kubernetes resources are defined in `deployment.yaml`.
- Each service typically runs as a **Deployment** controlling one or more **Pods**.
- Pods contain one container (or multiple, depending on the manifest) for:
  - the Streamlit dashboard
  - the frontend (often served by Nginx)
  - the form/ingestion service

Typical Kubernetes concepts referenced by this setup:

- **Pod**: smallest deployable unit (runs your container(s))
- **Deployment**: ensures desired replica count and supports rolling updates
- **Service**: provides stable networking between components
- **Ingress** (if configured in the manifest): routes external traffic to services

### Notes / Prerequisites

- Ensure Supabase credentials (`SUPABASE_URL`, `SUPABASE_KEY`) are provided to the relevant containers (env vars or Kubernetes Secrets).
- Confirm that the services expose the expected ports (Streamlit defaults to `8501`; Nginx uses its configured port).

---

## Getting Started

### Prerequisites

- Python 3.8+
- Supabase project (default data source)
- Environment variables: `SUPABASE_URL`, `SUPABASE_KEY`

Local CSV testing is supported via `USE_CSV = True` in `constants.py`.

### Installation

```bash
git clone https://github.com/Ak47xdd/Dashboard-Placed.git
cd Dashboard-Placed

python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### Configure `constants.py`

Key settings:

| Constant          | Description                              | Default                              |
| ----------------- | ---------------------------------------- | ------------------------------------ |
| `REFRESH_SECONDS` | Auto-refresh interval                    | `30`                                 |
| `USE_CSV`         | Toggle local CSV vs Supabase             | `False`                              |
| `MAIN_CSV`        | Local student dataset base name          | `"STUDENTS - Sheet1"`                |
| `CSV_FILE`        | Local classification dataset base name   | `"CLASSIFICATIONS - Sheet1 (1).csv"` |
| `SUPA_DB`         | Supabase table for classification        | `"CLASSIFICATION"`                   |
| `SUPA_RAW_DB`     | Supabase table for student raw responses | `"STUDENT_DATA"`                     |

### Running the App

```bash
streamlit run app.py
```

Local URL: `http://localhost:8501`

---

## Dashboard Views

### 1) Response Dashboard

- Intended for aggregated/classification insights.
- Uses the dataset from `SUPA_DB` (`CLASSIFICATION`) or the local CSV classification file when `USE_CSV=True`.

### 2) Student Evaluation Dashboard

- Student-level questionnaire analytics.
- Uses the raw dataset from `SUPA_RAW_DB` (`STUDENT_DATA`) or the local student CSV.
- Supports College/Department/Year filters + custom text filters.
- Displays learning-profile charts and engagement/commitment visualizations.
- Shows a cleaned **Student Responses** table and supports **Export CSV**.

---

## Expected Data Columns

The app consumes different subsets of columns depending on which view is active.

### Student Evaluation (raw `STUDENT_DATA`) expects (examples)

- Identity / grouping:
  - `student_id`, `student_name`
  - `college_name`, `department`, `course_type`, `year`
  - `medium`
- Placement/goal:
  - `career_goal`
  - `have_prep_test`
- Learning profile / questionnaire fields (examples used by charts):
  - `learn_Q1`
  - `instruct_Q1`, `instruct_Q2`, `instruct_Q3`, `instruct_Q4`, `instruct_Q5`, `instruct_Q6`
  - `content_pref_Q1`, `engage_Q1`, `engage_Q3`, `engage_Q4`
  - `commit_Q2`, `commit_Q4`
- Score analytics (if present):
  - `quant_score`, `logic_score`, `verbal_score`, `final_score`

### Response / Classification dataset (`CLASSIFICATION`)

The Response Dashboard is based on the classification table. Column expectations depend on your stored aggregation logic.

---

## How Auto-Refresh Works

- The app calls `auto_refresh()` from `frontend/styles.py`.
- `app.py` shows a **Refresh** button that:
  1. Clears `st.cache_data`
  2. Removes cached DataFrames from `st.session_state`
  3. Re-runs the app

---

## Troubleshooting

### Supabase authentication errors

- Ensure `SUPABASE_URL` and `SUPABASE_KEY` are correct.
- Verify table permissions for `CLASSIFICATION` and `STUDENT_DATA`.

### Data not loading / charts missing

- The Student Evaluation view shows informational messages when expected columns are missing (e.g., `learn_Q1`, `instruct_Q1`).
- Confirm your dataset column names match what the dashboard references.

### Auto-refresh issues

- Some browser environments restrict background refresh.
- Use the manual **Refresh** button in the app.

---

## License

MIT License. See `LICENSE` file for details.

---

## Acknowledgments

- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/python/)
