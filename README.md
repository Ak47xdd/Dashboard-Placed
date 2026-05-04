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

| Category        | Technology                                     |
| --------------- | ---------------------------------------------- |
| Frontend        | [Streamlit](https://streamlit.io/)             |
| Data Processing | [Pandas](https://pandas.pydata.org/)           |
| Visualizations  | [Plotly](https://plotly.com/python/)           |
| Data Source     | [Google Sheets](https://www.google.com/sheets) |
| API Integration | [gspread](https://gspread.readthedocs.io/)     |
| Authentication  | Google OAuth2                                  |

---

## Project Structure

```
Dashboard-Placed/
├── app.py                 # Main application entry point
├── client.py             # Google Sheets client configuration
├── constants.py          # Application constants and settings
├── filter.py            # Filter and visualization logic
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── .gitignore           # Git ignore rules
├── data/
│   ├── __init__.py
│   ├── data.py          # Data loading and processing
│   └── Placed_Dashboard - Form responses 1.csv  # Sample data
├── frontend/
│   ├── __init__.py
│   ├── bg.py            # Background image configuration
│   └── styles.py        # Custom CSS styling
└── Resources/
    ├── Placed_base64.txt    # Base64 encoded background image
    └── Placed.jpg          # Background image source
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Cloud service account credentials
- Google Sheets API enabled

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

4. Configure Google Sheets:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Sheets API and Google Drive API
   - Create a service account and download the JSON credentials
   - Rename the credentials file to `service_key.json`
   - Share your Google Sheet with the service account email

5. Configure constants:
   Edit `constants.py` to match your configuration:
   ```python
   SHEET_NAME = "Your_Sheet_Name"
   WORKSHEET_INDEX = 0
   REFRESH_SECONDS = 30
   (RECOMMENDED FOR TESTING)
   USE_CSV = False  # Set to True for local testing
   ```

### Running the Application

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

---

## Configuration

### Constants in `constants.py`

| Constant          | Description                            | Default Value                               |
| ----------------- | -------------------------------------- | ------------------------------------------- |
| `SHEET_NAME`      | Name of the Google Sheet               | `"Placed_Dashboard"`                        |
| `WORKSHEET_INDEX` | Index of the worksheet (0-indexed)     | `0`                                         |
| `REFRESH_SECONDS` | Auto-refresh interval in seconds       | `30`                                        |
| `USE_CSV`         | Use local CSV instead of Google Sheets | `False` or `True` for Local Tests           |
| `CSV_FILE`        | Path to local CSV file                 | `"Placed_Dashboard - Form responses 1.csv"` |

### Local Development Mode

To test with local CSV data:

1. Set `USE_CSV = True` in `constants.py`
2. Ensure the CSV file exists in the `data/` directory
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

1. Authentication Error
   - Ensure `service_key.json` is in the project root
   - Verify the service account has access to the Google Sheet

2. Data Not Loading
   - Check column names match the expected format
   - Verify the worksheet index is correct

3. Auto-Refresh Not Working
   - The meta refresh may be blocked by some browsers
   - Use the manual refresh button as an alternative

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the excellent web framework
- [gspread](https://gspread.readthedocs.io/) for Google Sheets integration
- [Plotly](https://plotly.com/python/) for interactive visualizations

---

## Support

For issues and feature requests, please open an issue on the project repository.

---
