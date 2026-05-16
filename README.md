# Dashboard-Placed

A Streamlit-based data analytics dashboard for tracking student placement data. This dashboard provides interactive visualizations, KPI metrics, and real-time data updates for monitoring student enrollment and placement statistics.

![Streamlit Version](https://img.shields.io/badge/Streamlit-1.57.0+-06B3C9?style=flat&logo=streamlit)
![Python Version](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python)

---

## Features

- Interactive Dashboard - Visual KPIs and metrics at a glance
- Multiple Filters - Filter by Department, Semester, Course, and College
- Rich Visualizations - Bar charts, pie charts, histograms, and trend lines
- Auto-Refresh - Automatic data updates every 30 seconds
- CSV Export - Export filtered data to CSV format
- Search Functionality - Search records by name, college, department, or course
- Custom Styling - Personalized background and UI enhancements

---

## Tech Stack

| Category        | Technology                                                              |
| --------------- | ----------------------------------------------------------------------- |
| Frontend        | [Streamlit](https://streamlit.io/)                                      |
| Data Processing | [Pandas](https://pandas.pydata.org/)                                    |
| Visualizations  | [Plotly](https://plotly.com/python/)                                    |
| Data Source     | [Supabase](https://supabase.com/) (default) / Local CSV (optional)      |
| API Integration | Supabase REST (no external supabase SDK)                                |
| Authentication  | Supabase JWT via environment variables (`SUPABASE_URL`, `SUPABASE_KEY`) |

---

## Project Structure (current)

```
Dashboard-Placed/
├── app.py               # Main application entry point
├── client.py            # Google Sheets client configuration
├── constants.py         # Application constants and settings
├── filter.py            # Filter and visualization logic
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── .gitignore           # Git ignore rules
├── data/
│   ├── __init__.py
│   └──  data.py         # Data loading and processing
├── frontend/
│   ├── __init__.py
│   ├── bg.py            # Background image configuration
│   └── styles.py        # Custom CSS styling
└── Resources/
    ├── Placed_base64.txt# Base64 encoded background image
    └── Placed.jpg       # Background image source
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Supabase project (default data source)
- Set environment variables `SUPABASE_URL` and `SUPABASE_KEY`

> Local CSV testing is supported by setting `USE_CSV = True` in `constants.py`.

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Dashboard-Placed
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   (OPTIONAL)

4. Configure Supabase (required when `USE_CSV = False`):
   - Set `SUPABASE_URL` and `SUPABASE_KEY` as environment variables
   - Ensure the Supabase tables exist and match `constants.py`:
     - `CLASSIFICATION` (aggregated dashboard data)
     - `STUDENT_DATA` (raw student/evaluation data)

5. Configure constants:
   Edit `constants.py` to match your configuration:
   ```python
   REFRESH_SECONDS = 30
   USE_CSV = False  # Set to True for local testing
   ```

# When using Supabase (USE_CSV=False):

# SUPA_DB and SUPA_RAW_DB default to "CLASSIFICATION" and "STUDENT_DATA"

### Running the Application

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

---

## Configuration

### Constants in `constants.py`

| Constant          | Description                                 | Default                              |
| ----------------- | ------------------------------------------- | ------------------------------------ |
| `REFRESH_SECONDS` | Auto-refresh interval (seconds)             | `30`                                 |
| `USE_CSV`         | Toggle data source (local CSV vs Supabase)  | `False`                              |
| `MAIN_CSV`        | Local CSV base name for student data        | `"STUDENTS - Sheet1"`                |
| `CSV_FILE`        | Local CSV base name for classification data | `"CLASSIFICATIONS - Sheet1 (1).csv"` |
| `SUPA_DB`         | Supabase table for classification           | `"CLASSIFICATION"`                   |
| `SUPA_RAW_DB`     | Supabase table for raw student data         | `"STUDENT_DATA"`                     |

### Local Development Mode (CSV)

To test with local CSV data:

1. Set `USE_CSV = True` in `constants.py`
2. Ensure the CSV files exist in the `data/` directory
3. Run `streamlit run app.py`

---

## Dashboard Features

### Interactive Filters

- Department/Class - Filter by academic department
- Semster/Section - Filter by semester
- Course - Filter by course name
- College - Filter by college/school name

### KPI Metrics

- Total Responses
- Unique Students
- Total Hours Spent
- Average Hours per Student
- Number of Colleges
- Number of Departments
- Number of Courses
- Latest Enrollment Date

### Visualizations

- Students by Department (Bar Chart)
- Students by College (Bar Chart)
- Students by Course (Bar Chart)
- Distribution by Semester (Pie Chart)
- Average Hours by Course (Bar Chart)
- Hours Distribution (Histogram)
- Enrollment Trend Over Time (Line Chart)

### Data Table

- Searchable data grid
- Export to CSV functionality
- Pagination support

---

## Expected Data Format

The Google Sheet/CSV should contain the following columns:

| Column                    | Description          |
| ------------------------- | -------------------- |
| Full Name                 | Student's full name  |
| Department/Class          | Academic department  |
| Semster/Section           | Semester and section |
| Course                    | Course name          |
| College Name/ School Name | College/school name  |
| Hours spent               | Total hours spent    |
| Date of Enrollment        | Date of enrollment   |
| Timestamp                 | Response timestamp   |

---

## Troubleshooting

### Common Issues

1. Supabase authentication error
   - Ensure `SUPABASE_URL` and `SUPABASE_KEY` are set in your environment
   - Verify the Supabase project/table access permissions

2. Data Not Loading
   - Check column names/types match what the dashboard expects
   - Verify your Supabase tables (or local CSVs) are populated

3. Auto-refresh not working
   - Use the manual “Refresh” button in the app (browser restrictions may limit background refresh)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the excellent web framework

- [Plotly](https://plotly.com/python/) for interactive visualizations

---

## Support

For issues and feature requests, please open an issue on the project repository.

---
