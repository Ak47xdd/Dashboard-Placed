import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
 
from college_dept_map import COLLEGE_VARIANT_CANONICAL_MAP, DEPARTMENT_VARIANT_CANONICAL_MAP
 
# =============== Constants ===============
 
ZERO_VARIANCE_COLS = [
    "learn_Q3",
    "learn_Q4",
    "instruct_Q2",
    "instruct_Q3",
    "instruct_Q4",
    "commit_Q1",
    "commit_Q4",
]
 
DF_COLS_TO_DROP = [
    "quant_Q1", "quant_Q2", "quant_Q3", "quant_Q4", "quant_Q5",
    "logic_Q1", "logic_Q2", "logic_Q3", "logic_Q4", "logic_Q5",
    "verbal_Q1", "verbal_Q2", "verbal_Q3", "verbal_Q4", "verbal_Q5",
    "behave_Q1", "behave_Q2", "behave_Q3", "behave_Q4", "behave_Q5",
    "commit_Q3",
]
 
# Consistent chart height used across every figure so rows align
CHART_H = 400
 
# Build lowercase lookup maps once at module load — not inside every call
_COLLEGE_LOWER_MAP = {k.lower(): v for k, v in COLLEGE_VARIANT_CANONICAL_MAP.items()}
_DEPT_LOWER_MAP    = {k.lower(): v for k, v in DEPARTMENT_VARIANT_CANONICAL_MAP.items()}
 
 
# =============== Helpers ===============
 
def _normalize_college_name(series: pd.Series) -> pd.Series:
    """Normalize a college_name series using the module-level canonical map."""
    if series is None:
        return series
    s = series.fillna("").astype(str).str.strip()
    if not _COLLEGE_LOWER_MAP:
        return s
    s_lower = s.str.lower()
    for wrong_lower, canonical in _COLLEGE_LOWER_MAP.items():
        mask = s_lower.eq(wrong_lower)
        if mask.any():
            s.loc[mask] = canonical
    return s
 
 
def _normalize_dept_name(series: pd.Series) -> pd.Series:
    """Normalize a department series using the module-level canonical map."""
    if series is None:
        return series
    s = series.fillna("").astype(str).str.strip()
    if not _DEPT_LOWER_MAP:
        return s
    s_lower = s.str.lower()
    for wrong_lower, canonical in _DEPT_LOWER_MAP.items():
        mask = s_lower.eq(wrong_lower)
        if mask.any():
            s.loc[mask] = canonical
    return s
 
 
def _value_counts_df(series: pd.Series, name: str) -> pd.DataFrame:
    vc = series.dropna().astype(str).value_counts().reset_index()
    vc.columns = [name, "count"]
    return vc
 
 
# =============== Section 3 sub-renderers ===============
 
def _render_seek_answers_bar(df: pd.DataFrame) -> None:
    """
    Chart 3A — Full-width single-row stacked bar.
    Answers: 'How do students seek answers when stuck?'
    One glance shows the split — no axes, no numbers to decode.
    """
    if "learn_Q1" not in df.columns:
        st.info("Missing learn_Q1 column.")
        return
 
    counts = _value_counts_df(df["learn_Q1"], "learn_Q1")
    total  = counts["count"].sum()
    counts["pct"] = (counts["count"] / total * 100).round(1)
 
    fig = go.Figure()
    colors = px.colors.qualitative.Pastel
    for i, row in counts.iterrows():
        label = row["learn_Q1"]
        n     = row["count"]
        pct   = row["pct"]
        fig.add_trace(go.Bar(
            x=[n],
            y=["Students"],
            orientation="h",
            name=label,
            text=f"{label}<br>{n} student{'s' if n != 1 else ''} ({pct}%)",
            textposition="inside",
            insidetextanchor="middle",
            marker_color=colors[i % len(colors)],
            hovertemplate=f"<b>{label}</b><br>{n} students ({pct}%)<extra></extra>",
        ))
 
    fig.update_layout(
        barmode="stack",
        title="How do students seek answers when stuck?",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="left", x=0),
        height=140,
        margin=dict(t=70, b=10, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")
 
 
def _render_teaching_style_bubble(df: pd.DataFrame) -> None:
    """
    Chart 3B — Bubble matrix.
    X = preferred teaching approach (instruct_Q1)
    Y = self-assessment confidence (instruct_Q6)
    Bubble size = number of students at that combination
    Color = feedback timing preference (instruct_Q5)
 
    Answers: 'What teaching style fits them?'
    Bigger bubbles = where most students cluster.
    """
    needed = ["instruct_Q1", "instruct_Q6"]
    if not all(c in df.columns for c in needed):
        st.info("Missing instruct_Q1 or instruct_Q6 columns.")
        return
 
    color_col  = "instruct_Q5" if "instruct_Q5" in df.columns else None
    group_cols = needed + ([color_col] if color_col else [])
 
    agg = (
        df[group_cols]
        .dropna()
        .astype(str)
        .groupby(group_cols)
        .size()
        .reset_index(name="count")
    )
 
    if agg.empty:
        st.info("Not enough data for teaching style chart.")
        return
 
    confidence_order = ["Low", "Medium", "High"]
    agg["instruct_Q6"] = pd.Categorical(
        agg["instruct_Q6"], categories=confidence_order, ordered=True
    )
    agg = agg.sort_values("instruct_Q6")
 
    fig = px.scatter(
        agg,
        x="instruct_Q1",
        y="instruct_Q6",
        size="count",
        color=color_col,
        size_max=60,
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={
            "instruct_Q1": "Preferred Teaching Approach",
            "instruct_Q6": "Self-Assessment Confidence",
            "instruct_Q5": "Feedback Timing",
            "count":       "Students",
        },
        title="What teaching style fits them?",
        hover_data={"count": True, "instruct_Q1": True, "instruct_Q6": True},
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="white")))
    fig.update_layout(
        height=CHART_H,
        margin=dict(t=50, b=60, l=10, r=10),
        xaxis_tickangle=-20,
        legend_title_text="Feedback Timing" if color_col else "",
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="right", x=0.5),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")
 
 
def _render_content_engage_donuts(df: pd.DataFrame) -> None:
    """
    Chart 3C — Two small donuts stacked vertically inside a single column.
    Top:    content_pref_Q1 — preferred content format
    Bottom: engage_Q1       — preferred activity style
 
    Answers: 'What content and activities do they prefer?'
    Sits in the right column next to Chart 3B.
    """
    left_col  = "content_pref_Q1"
    right_col = "engage_Q1"
 
    has_left  = left_col  in df.columns
    has_right = right_col in df.columns
 
    if not has_left and not has_right:
        st.info("Missing content_pref_Q1 and engage_Q1 columns.")
        return
 
    if has_left:
        counts = _value_counts_df(df[left_col], left_col)
        fig = px.pie(
            counts, names=left_col, values="count", hole=0.5,
            title="Preferred content format",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(
            showlegend=False,
            height=CHART_H // 2,
            margin=dict(t=40, b=20, l=40, r=40),
        )
        st.plotly_chart(fig, width="stretch")
 
    if has_right:
        counts = _value_counts_df(df[right_col], right_col)
        fig = px.pie(
            counts, names=right_col, values="count", hole=0.5,
            title="Preferred activity style",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(
            showlegend=False,
            height=CHART_H // 2,
            margin=dict(t=40, b=20, l=40, r=40),
        )
        st.plotly_chart(fig, width="stretch")

# =============== Main render ===============
 
def render_student_tab(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        st.info("No student data available.")
        return
 
    # df arrives already normalized from db_queries.fetch_student_raw_df()
    # No _normalize() call needed here.
 
    # Session state defaults
    defaults = {
        'selected_colleges': [],
        'custom_college': '',
        'selected_depts': [],
        'custom_dept': '',
        'selected_years': [],
        'custom_year': ''
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
 
    # =============== Filters ===============
    st.markdown(
        """
        <div class="main-filter-section">
            <h2 class="main-filter-title">College & Program Filters</h2>
            <p class="filter-subtitle">Select colleges, departments, years or type custom values. Leave empty to show all.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
 
    filter_container = st.container()
    with filter_container:
        col1, col2, col3 = st.columns(3)
 
        with col1:
            colleges = (
                sorted(df['college_name'].dropna().unique().tolist())
                if 'college_name' in df.columns else []
            )
            colleges = [_normalize_college_name(pd.Series([c])).iloc[0] for c in colleges]
 
            selected_colleges = st.multiselect(
                "Colleges", colleges,
                default=st.session_state.get('selected_colleges', []),
                key='college_multiselect',
                help="Click dropdown or type to search colleges",
            )
            custom_college = st.text_input(
                "Custom college name",
                value=st.session_state.get('custom_college', ''),
                key='custom_college_input',
                placeholder="Type exact name e.g., 'New College'",
                help="Filters students from exactly this college name",
            )
            if custom_college.strip():
                custom_college = _normalize_college_name(pd.Series([custom_college])).iloc[0]
            if isinstance(selected_colleges, list):
                selected_colleges = [_normalize_college_name(pd.Series([c])).iloc[0] for c in selected_colleges]
                st.session_state['selected_colleges'] = selected_colleges
 
        with col2:
            depts = (
                sorted(df['department'].dropna().unique().tolist())
                if 'department' in df.columns else []
            )
            selected_depts = st.multiselect(
                "Department", depts,
                default=st.session_state.get('selected_depts', []),
                key='dept_multiselect',
                help="Click dropdown or type to search departments",
            )
            custom_dept = st.text_input(
                "Custom department",
                value=st.session_state.get('custom_dept', ''),
                key='custom_dept_input',
                placeholder="e.g., 'BTech CS', 'MCA'",
            )
 
        with col3:
            years = (
                sorted(df['year'].dropna().unique().tolist())
                if 'year' in df.columns else []
            )
            selected_years = st.multiselect(
                "Year", years,
                default=st.session_state.get('selected_years', []),
                key='year_multiselect',
                help="Click dropdown or type year numbers",
            )
            custom_year = st.text_input(
                "Custom year",
                value=st.session_state.get('custom_year', ''),
                key='custom_year_input',
                placeholder="e.g., '1', '4'",
            )
 
    # Apply filters
    filtered_df = df.copy()
 
    all_colleges = list(selected_colleges) if isinstance(selected_colleges, list) else []
    if isinstance(custom_college, str) and custom_college.strip():
        all_colleges.append(custom_college.strip())
    if all_colleges and 'college_name' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['college_name'].str.contains('|'.join(all_colleges), case=False, na=False)
        ]
 
    all_depts = list(selected_depts) if isinstance(selected_depts, list) else []
    if isinstance(custom_dept, str) and custom_dept.strip():
        custom_dept = _normalize_dept_name(pd.Series([custom_dept])).iloc[0]
        all_depts.append(custom_dept.strip())
    if all_depts and 'department' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['department'].str.contains('|'.join(all_depts), case=False, na=False)
        ]
 
    all_years_str = [str(y) for y in selected_years] if isinstance(selected_years, list) else []
    if isinstance(custom_year, str) and custom_year.strip():
        all_years_str.append(custom_year.strip())
    if all_years_str and 'year' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['year'].astype(str).str.contains('|'.join(all_years_str), case=False, na=False)
        ]
 
    # Filter summary
    filter_summary = []
    if selected_colleges or (isinstance(custom_college, str) and custom_college.strip()):
        filter_summary.append(f"College: {', '.join(selected_colleges[:2])}{'...' if len(selected_colleges)>2 else ''}{' + custom' if (isinstance(custom_college, str) and custom_college.strip()) else ''}")
    if selected_depts or (isinstance(custom_dept, str) and custom_dept.strip()):
        filter_summary.append(f"Dept: {', '.join(selected_depts[:2])}{'...' if len(selected_depts)>2 else ''}{' + custom' if (isinstance(custom_dept, str) and custom_dept.strip()) else ''}")
    if selected_years or (isinstance(custom_year, str) and custom_year.strip()):
        filter_summary.append(f"Year: {', '.join(map(str, selected_years[:2]))}{'...' if len(selected_years)>2 else ''}{' + custom' if (isinstance(custom_year, str) and custom_year.strip()) else ''}")
 
    col_summary1, col_summary2 = st.columns([3, 1])
    with col_summary1:
        st.markdown(
            f"""
            <div class="filter-stats">
                <strong>Showing {len(filtered_df)} of {len(df)} students</strong>
                {' | Filters: ' + ' | '.join(filter_summary) if filter_summary else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_summary2:
        if st.button("Clear All Filters", key="clear_filters_btn"):
            for k in ['selected_colleges', 'custom_college', 'selected_depts',
                      'custom_dept', 'selected_years', 'custom_year']:
                st.session_state[k] = [] if k.startswith('selected') else ''
            st.rerun()
 
    if filtered_df.empty:
        st.warning("No students match your filters!")
        st.info("Leave dropdowns empty to show all students, or check your custom text spelling.")
        st.stop()
 
    st.session_state.selected_colleges = selected_colleges
    st.session_state.custom_college    = custom_college if isinstance(custom_college, str) else ''
    st.session_state.selected_depts    = selected_depts
    st.session_state.custom_dept       = custom_dept if isinstance(custom_dept, str) else ''
    st.session_state.selected_years    = selected_years
    st.session_state.custom_year       = custom_year if isinstance(custom_year, str) else ''
 
    df = filtered_df

    # Map instruct_Q2 / instruct_Q3 numeric codes (1..4) to labels.
    # Dashboard expects High/Medium/Low/None for display/heatmaps.
    try:
        from questionnaire_instruct_map import normalize_instruct_value

        inv_map = {1: "High", 2: "Medium", 3: "Low", 4: "None"}
        for q in ["instruct_Q2", "instruct_Q3"]:
            if q in df.columns:
                df[q] = df[q].apply(normalize_instruct_value).map(inv_map)
    except Exception:
        pass

    # =============== KPI Row ===============

    placement_pct = 0.0
    if "career_goal" in df.columns:
        placement_pct = (
            df["career_goal"].astype(str).str.lower().str.contains("placement").mean() * 100
        )
 
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Students",           len(df))
    k2.metric("Colleges",                 df["college_name"].nunique() if "college_name" in df.columns else "-")
    k3.metric("Departments",              df["department"].nunique()   if "department"   in df.columns else "-")
    k4.metric("In-Campus Placement Seekers", f"{placement_pct:.0f}%")
 
    st.markdown("---")
 
    # =============== Section 1 — Who Are They? ===============
    st.subheader("Student Demographics & Background")
 
    col1, col2 = st.columns([2, 1])
 
    with col1:
        if all(c in df.columns for c in ["college_name", "department", "year"]):
            fig = px.sunburst(
                df,
                path=["college_name", "department", "year"],
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="College → Department → Year Distribution",
            )
            fig.update_layout(height=CHART_H, margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Missing college_name / department / year columns.")
 
    with col2:
        if "medium" in df.columns:
            counts = _value_counts_df(df["medium"], "medium")
            fig = px.pie(
                counts, names="medium", values="count", hole=0.45,
                title="Medium of Instruction",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_traces(textposition="outside", textinfo="percent+label")
            fig.update_layout(
                height=CHART_H,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                margin=dict(t=40, b=40, l=10, r=10),
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Missing medium column.")
 
    st.markdown("---")
 
    # =============== Section 2 — Goals & Readiness ===============
    st.subheader("Goals & Readiness")
 
    col1, col2 = st.columns(2)
 
    with col1:
        if all(c in df.columns for c in ["career_goal", "have_prep_test"]):
            tmp = df[["career_goal", "have_prep_test"]].dropna().astype(str).copy()
            fig = px.bar(
                tmp, y="career_goal", color="have_prep_test",
                orientation="h", barmode="group",
                title="Career Goals vs Prep Test Status",
                color_discrete_sequence=px.colors.qualitative.Bold,
                labels={"career_goal": "", "have_prep_test": "Prep Test"},
            )
            fig.update_layout(
                height=CHART_H,
                xaxis_title="Number of Students",
                legend_title_text="Prep Test Taken",
                legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="right", x=0.5),
                margin=dict(t=50, b=70, l=10, r=10),
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Missing career_goal and/or have_prep_test columns.")
 
    with col2:
        if "career_goal" in df.columns:
            counts = _value_counts_df(df["career_goal"], "career_goal")
            fig = px.pie(
                counts, names="career_goal", values="count", hole=0.45,
                title="Career Goal Distribution",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig.update_traces(textposition="outside", textinfo="percent+label")
            fig.update_layout(
                height=CHART_H, showlegend=False,
                margin=dict(t=50, b=40, l=60, r=60),
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Missing career_goal column.")
 
    st.markdown("---")
 
    # =============== Section 3 — Learning Profile ===============
    st.subheader("Learning Profile")
 
    _render_seek_answers_bar(df)
    st.markdown(" ")
 
    col_b, col_c = st.columns(2)
    with col_b:
        _render_teaching_style_bubble(df)
    with col_c:
        _render_content_engage_donuts(df)
 
    st.markdown("---")
 
    # =============== Section 4 — Engagement & Commitment ===============
    st.subheader("Engagement & Commitment")
 
    col1, col2 = st.columns(2)
 
    with col1:
        if "engage_Q3" in df.columns:
            counts = _value_counts_df(df["engage_Q3"], "engage_Q3")
            fig = px.bar(
                counts, x="count", y="engage_Q3",
                orientation="h",
                color="count", color_continuous_scale="Viridis",
                title="What motivates students to engage?",
                labels={"engage_Q3": "", "count": "Students"},
            )
            fig.update_layout(
                height=CHART_H,
                xaxis_title="Number of Students",
                coloraxis_showscale=False,
                margin=dict(t=50, b=20, l=10, r=10),
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Missing engage_Q3 column.")
 
    with col2:
        if "commit_Q2" in df.columns:
            counts = _value_counts_df(df["commit_Q2"], "commit_Q2")
            fig = px.pie(
                counts, names="commit_Q2", values="count", hole=0.45,
                title="What blocks students from committing?",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig.update_traces(textposition="outside", textinfo="percent+label")
            fig.update_layout(
                height=CHART_H, showlegend=False,
                margin=dict(t=50, b=40, l=60, r=60),
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Missing commit_Q2 column.")
 
    if all(c in df.columns for c in ["engage_Q1", "engage_Q4"]):
        tmp = df[["engage_Q1", "engage_Q4"]].dropna().astype(str).copy()
        if not tmp.empty:
            fig = px.bar(
                tmp, x="engage_Q1", color="engage_Q4", barmode="stack",
                title="Preferred activity style vs what students want added to sessions",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={"engage_Q1": "", "engage_Q4": "Wants Added"},
            )
            fig.update_layout(
                height=CHART_H,
                yaxis_title="Number of Students",
                legend_title_text="What they want added",
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                margin=dict(t=50, b=80, l=10, r=10),
            )
            st.plotly_chart(fig, width="stretch")
 
    st.markdown("---")
 
    # =============== Data Table ===============
    st.subheader("Student Responses")
 
    cols_to_drop = set(DF_COLS_TO_DROP) | {
        "quant_score", "logic_score", "verbal_score", "final_score", "created_at"
    }
    table_df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
 
    identity_order = [
        "student_id", "student_name", "college_name", "department",
        "course_type", "year", "medium",
    ]
    ordered  = [c for c in identity_order if c in table_df.columns]
    rest     = [c for c in table_df.columns if c not in ordered]
    table_df = table_df[ordered + rest]
 
    if "student_id" in table_df.columns:
        table_df["student_id"] = table_df["student_id"].fillna("").astype(str)
        student_ids = sorted(table_df["student_id"].drop_duplicates().tolist())
 
        col_sel, col_toggle = st.columns([4, 1])
        with col_sel:
            selected_id = st.selectbox("Filter by Student ID", options=student_ids, index=0)
        with col_toggle:
            show_one = st.checkbox("Show one", value=True)
 
        if show_one:
            st.dataframe(
                table_df[table_df["student_id"] == selected_id].reset_index(drop=True),
                width="stretch",
            )
        else:
            st.dataframe(table_df.reset_index(drop=True), width="stretch")
    else:
        st.dataframe(table_df.reset_index(drop=True), width="stretch")