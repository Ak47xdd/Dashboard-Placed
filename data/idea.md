fr# Student Dashboard — Visualization Strategy

## Overview

The `STUDENT_DATA` table (synced from Supabase via `db_queries.py`) contains **34 columns** across 7 students (as of profiling). The data is a profiling questionnaire — no scores, no numeric performance data. Every insight comes from categorical responses. This document covers what to build, why, what to skip, and how to wire it into the existing Streamlit dashboard.

---

## Data Schema

| Group                      | Columns                                                                                     | What they capture                                |
| -------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Identity**               | `student_id`, `student_name`, `college_name`, `department`, `course_type`, `year`, `medium` | Who the student is                               |
| **Readiness**              | `have_prep_test`, `career_goal`                                                             | What they want and whether they've acted on it   |
| **Learning style**         | `learn_Q1`, `learn_Q2`, `learn_Q3`, `learn_Q4`                                              | How they seek knowledge independently            |
| **Instruction preference** | `instruct_Q1` – `instruct_Q6`                                                               | What teaching style works for them               |
| **Content preference**     | `content_pref_Q1`, `content_pref_Q2`, `content_pref_Q3`                                     | How they prefer to consume material              |
| **Engagement**             | `engage_Q1`, `engage_Q2`, `engage_Q3`, `engage_Q4`                                          | What kind of learning activities they respond to |
| **Commitment**             | `commit_Q1`, `commit_Q2`, `commit_Q4`                                                       | How committed they are and what blocks them      |

---

## Zero-Variance Columns — Skip These

The following columns had **identical answers from every single student** in the current dataset. Visualizing them produces useless single-bar charts. Exclude them from all charts.

| Column        | Uniform value        | Why it's useless |
| ------------- | -------------------- | ---------------- |
| `learn_Q3`    | "Balanced"           | 7/7 same answer  |
| `learn_Q4`    | "Try another method" | 7/7 same answer  |
| `instruct_Q2` | "Low"                | 7/7 same answer  |
| `instruct_Q3` | "Low"                | 7/7 same answer  |
| `instruct_Q4` | "10"                 | 7/7 same answer  |
| `commit_Q1`   | "3"                  | 7/7 same answer  |
| `commit_Q4`   | "Yes"                | 7/7 same answer  |

> These may gain variance as more students fill the form. Re-evaluate once `n > 50`.

---

## Columns with Real Signal

These have variation and are worth visualizing:

```
learn_Q1, learn_Q2
instruct_Q1, instruct_Q5, instruct_Q6
content_pref_Q1, content_pref_Q2, content_pref_Q3
engage_Q1, engage_Q2, engage_Q3, engage_Q4
commit_Q2
have_prep_test, career_goal
college_name, department, course_type, year, medium
```

---

## Dashboard Structure

Split the student tab into **4 sections**, each with a clear question it answers.

---

### Section 1 — Who Are They?

**Question answered:** What is the demographic breakdown of the cohort?

#### Chart 1A — Sunburst: College → Department → Year

```python
px.sunburst(df, path=['college_name', 'department', 'year'])
```

- Replaces 3 separate bar charts in one drillable view
- Click a college segment to zoom into its departments and years
- Use `px.colors.qualitative.Pastel` for soft, readable colors

#### Chart 1B — Donut: Medium of Instruction

```python
px.pie(df['medium'].value_counts().reset_index(),
       names='medium', values='count', hole=0.45)
```

- English vs Malayalam split
- Small chart, sits beside the sunburst in a 2-column row
- Add a center annotation with total student count

**Layout:** `col1 (2/3 width) = Sunburst | col2 (1/3 width) = Donut`

---

### Section 2 — Goals & Readiness

**Question answered:** What do students want, and are they acting on it?

#### Chart 2A — Grouped Horizontal Bar: Career Goal × Prep Test Status

```python
px.bar(df, y='career_goal', color='have_prep_test',
       orientation='h', barmode='group')
```

- The key insight: are students pursuing Campus Placements actually taking prep tests?
- Color by `have_prep_test` (Yes-Basic vs No) — two-tone, immediately readable
- Sort bars by total count descending

#### Chart 2B — Donut: Career Goal Distribution

```python
px.pie(df['career_goal'].value_counts().reset_index(),
       names='career_goal', values='count', hole=0.45)
```

- Sits beside Chart 2A
- Shows whether the cohort skews placement-focused, higher-studies, or undecided

**Layout:** `col1 = Grouped bar | col2 = Donut`

---

### Section 3 — Learning Profile _(Most Important Section)_

**Question answered:** How do students learn, and what do they need from instruction?

#### Chart 3A — Parallel Categories: Full Learning Flow

```python
px.parallel_categories(
    df,
    dimensions=['learn_Q1', 'instruct_Q1', 'content_pref_Q1', 'engage_Q1'],
    color=df['career_goal'].astype('category').cat.codes,
    color_continuous_scale=px.colors.sequential.Inferno
)
```

- **This is the standout chart for this dataset.** It draws Sankey-style flow lines from how a student seeks answers → preferred instruction style → content format → engagement type.
- Color lines by `career_goal` to see if placement-seekers cluster into specific learning patterns
- Full width row — doesn't need a column partner
- Readable insight example: "Search online → Concept explanation → Visual → Activity-based" is the dominant flow

#### Chart 3B — Response Frequency Heatmap

```python
# Build a question × response frequency matrix
questions = ['learn_Q1','learn_Q2','instruct_Q1','instruct_Q5',
             'instruct_Q6','content_pref_Q1','engage_Q1','engage_Q2','commit_Q2']
# For each question, get value_counts as %, pivot into matrix
px.imshow(matrix, text_auto=True, color_continuous_scale='YlOrRd', aspect='auto')
```

- Compact overview of all question responses in one grid
- Rows = questions, Columns = response options, Values = % of students
- Immediately shows the dominant answer per question and which questions have the most spread
- Full width, placed below the parallel categories chart

**Layout:** `Parallel Categories (full width)` → `Heatmap (full width)`

---

### Section 4 — Engagement & Commitment

**Question answered:** What drives and blocks student engagement?

#### Chart 4A — Horizontal Bar: What Motivates Engagement (`engage_Q3`)

```python
px.bar(engage_counts, x='count', y='engage_Q3', orientation='h',
       color='count', color_continuous_scale='Viridis')
```

- Practical application vs Competition vs Participation
- One of the few places a bar chart is genuinely appropriate — single categorical frequency
- Sort by count descending

#### Chart 4B — Donut: Main Barrier (`commit_Q2`)

```python
px.pie(df['commit_Q2'].value_counts().reset_index(),
       names='commit_Q2', values='count', hole=0.45)
```

- Interest vs Time vs Motivation vs Guidance
- Directly tells you what's blocking students — actionable for PLACED's product team
- Use distinct colors: red = Time, yellow = Motivation, green = Interest, blue = Guidance

#### Chart 4C — Stacked Bar: Engagement Style Breakdown (`engage_Q1` × `engage_Q4`)

```python
px.bar(df, x='engage_Q1', color='engage_Q4', barmode='stack')
```

- Cross-tab preferred activity type vs what they want added to sessions
- Shows whether "Activity-based" learners also want "More interaction" or "Add activities"

**Layout:** `col1 = Horizontal bar | col2 = Donut` → `Stacked bar (full width)`

---

## KPI Row (Top of Tab)

Place 5 metric cards at the very top before any charts:

```python
k1.metric("👥 Total Students", len(df))
k2.metric("🏫 Colleges", df['college_name'].nunique())
k3.metric("📚 Departments", df['department'].nunique())
k4.metric("✅ Prep Test Taken", f"{prep_pct:.0f}%")
k5.metric("🎯 Placement Seekers", f"{placement_pct:.0f}%")
```

---

## Data Volume Warning

With fewer than ~20 students, every percentage is a multiple of 5–14%. Add this banner at the top of the tab when `len(df) < 20`:

```python
if len(df) < 20:
    st.warning(
        f"⚠️ Only {len(df)} students in the dataset. "
        "Distributions are not stable yet — patterns will be meaningful once n ≥ 50."
    )
```

---

## Integration with Existing `filter.py`

The existing `filter_data(df, view="raw")` already handles College / Department / Year filters and normalization via `COLLEGE_VARIANT_CANONICAL_MAP`. The student tab should:

1. Call `get_student_raw_data()` from `db_queries.py` (already written, uses `requests` against Supabase REST API with pagination)
2. Pass the result to `render_student_tab(df)` in `student_dashboard.py`
3. `render_student_tab` runs the same normalization logic from `filter.py` internally (already implemented via `_normalize()`) — **do not call `filter_data()` for the student tab**, it's built for the classification view

---

## File Map

| File                   | Status       | Change                                                                |
| ---------------------- | ------------ | --------------------------------------------------------------------- |
| `constants.py`         | ✅ Done      | Added `SUPA_RAW_DB = "STUDENT_DATA"`                                  |
| `db_queries.py`        | ✅ Done      | `get_student_raw_data()` via `requests`, paginated, score computation |
| `app.py`               | ✅ Done      | Two tabs: `📊 Score Classifications` and `🎓 Student Explorer`        |
| `student_dashboard.py` | 🔲 To build  | Implements all charts in this document                                |
| `filter.py`            | ✅ Unchanged | Classification tab only                                               |
| `college_dept_map.py`  | ✅ Unchanged | Shared by both tabs                                                   |

---

## Chart Selection Rationale

| Chart type             | Used for                      | Why not a bar chart                                    |
| ---------------------- | ----------------------------- | ------------------------------------------------------ |
| Sunburst               | College → Dept → Year         | Encodes 3 dimensions; bar needs 3 separate charts      |
| Parallel Categories    | Learning flow across 4 Qs     | Only chart type that shows multi-step categorical flow |
| Heatmap                | All question frequencies      | Compact; shows spread across all Qs at once            |
| Grouped horizontal bar | Career goal × prep status     | Horizontal is easier to read with long category labels |
| Stacked bar            | Engagement cross-tab          | Composition within category — bar is appropriate here  |
| Donut                  | Medium, career goal, barriers | Part-of-whole framing; hole allows center annotation   |

---

## Priority Order for Implementation

1. **Parallel Categories chart** — highest unique insight value, nothing else shows the learning flow
2. **KPI row** — fast to build, immediately useful
3. **Sunburst** — replaces 3 charts at once
4. **Heatmap** — best overview of all questionnaire responses
5. **Goals & Readiness section** — directly actionable for the product team
6. **Engagement & Commitment section** — deeper analysis, build last
