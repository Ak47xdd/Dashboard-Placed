"""
Filters for Response Dashboard/Student Evaluation Dashboard.:
This module implements the filtering logic for the Dashboard, 
allowing users to filter student data by college, department, year, and other criteria. 
It also handles normalization of college and department names to ensure consistent filtering and accurate charting.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from constants import REFRESH_SECONDS
from datetime import datetime
from filters.student_dashboard import render_student_tab
from filters.college_dept_map import COLLEGE_VARIANT_CANONICAL_MAP, DEPARTMENT_VARIANT_CANONICAL_MAP

# Build lowercase lookup maps (refer college_dept_map.py for the canonical maps and their maintenance)
_COLLEGE_LOWER_MAP = {k.lower(): v for k, v in COLLEGE_VARIANT_CANONICAL_MAP.items()}
_DEPT_LOWER_MAP    = {k.lower(): v for k, v in DEPARTMENT_VARIANT_CANONICAL_MAP.items()}

def _normalize_college_name(series):
    """
    Normalize college_name using the module-level canonical map.
    """
    
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

def filter_data(df, view: str = "classification"):
    
    init_session_state()

    if view == "raw":
        render_student_tab(df)
        return
 
    filtered_df = df.copy()
 
    if 'college_name' in filtered_df.columns:
        filtered_df['college_name'] = (
            filtered_df['college_name'].fillna('').astype(str).str.strip()
        )
        cn = filtered_df['college_name'].str.lower()
        for wrong_lower, canonical in _COLLEGE_LOWER_MAP.items():
            mask = cn.eq(wrong_lower)
            if mask.any():
                filtered_df.loc[mask, 'college_name'] = canonical
        filtered_df['college_name'] = filtered_df['college_name'].astype(str).str.strip()
 
    if 'department' in filtered_df.columns:
        filtered_df['department'] = (
            filtered_df['department'].fillna('').astype(str).str.strip()
        )
        dn = filtered_df['department'].str.lower()
        for wrong_lower, canonical in _DEPT_LOWER_MAP.items():
            mask = dn.eq(wrong_lower)
            if mask.any():
                filtered_df.loc[mask, 'department'] = canonical
        filtered_df['department'] = filtered_df['department'].astype(str).str.strip()
 
    # ===== CATEGORICAL FILTERS ONLY (College, Department, Year) =====
 
    st.markdown("""
    <div class="main-filter-section">
        <h2 class="main-filter-title">College & Program Filters</h2>
        <p class="filter-subtitle">Select colleges, departments, years or type custom values. Leave empty to show all.</p>
    </div>
    """, unsafe_allow_html=True)
 
    filter_container = st.container()
    with filter_container:
        col1, col2, col3 = st.columns(3)
 
        with col1:
            colleges = (
                sorted(filtered_df['college_name'].dropna().unique().tolist())
                if 'college_name' in filtered_df.columns
                else []
            )
            # Re-normalize dropdown labels using module-level map (no dict rebuild)
            colleges = [_normalize_college_name(pd.Series([c])).iloc[0] for c in colleges]
 
            selected_colleges = st.multiselect(
                "College", colleges,
                default=st.session_state.get('selected_colleges', []),
                key='college_multiselect',
                help="Click dropdown or type to search colleges"
            )
 
            custom_college = st.text_input(
                "Custom college name",
                value=st.session_state.get('custom_college', ''),
                key='custom_college_input',
                placeholder="Type exact name e.g., 'New College'",
                help="Filters students from exactly this college name"
            )
 
            if custom_college.strip():
                custom_college = _normalize_college_name(pd.Series([custom_college])).iloc[0]
 
            if isinstance(selected_colleges, list):
                selected_colleges = [_normalize_college_name(pd.Series([c])).iloc[0] for c in selected_colleges]
                st.session_state['selected_colleges'] = selected_colleges
 
        with col2:
            depts = sorted(filtered_df['department'].dropna().unique().tolist()) if 'department' in filtered_df.columns else []
            selected_depts = st.multiselect(
                "Department", depts,
                default=st.session_state.get('selected_depts', []),
                key='dept_multiselect',
                help="Click dropdown or type to search departments"
            )
 
            custom_dept = st.text_input(
                "Custom department",
                value=st.session_state.get('custom_dept', ''),
                key='custom_dept_input',
                placeholder="e.g., 'BTech CS', 'MCA'"
            )
 
        with col3:
            years = sorted(filtered_df['year'].dropna().unique().tolist()) if 'year' in filtered_df.columns else []
            selected_years = st.multiselect(
                "Year", years,
                default=st.session_state.get('selected_years', []),
                key='year_multiselect',
                help="Click dropdown or type year numbers"
            )
 
            custom_year = st.text_input(
                "Custom year",
                value=st.session_state.get('custom_year', ''),
                key='custom_year_input',
                placeholder="e.g., '1', '4'"
            )
 
    all_colleges = selected_colleges.copy()
    if custom_college.strip():
        all_colleges.append(custom_college.strip())
    if all_colleges:
        filtered_df = filtered_df[filtered_df['college_name'].str.contains('|'.join(all_colleges), case=False, na=False)]
 
    all_depts = selected_depts.copy()
    if custom_dept.strip():
        all_depts.append(custom_dept.strip())
    if all_depts:
        filtered_df = filtered_df[filtered_df['department'].str.contains('|'.join(all_depts), case=False, na=False)]
 
    all_years_str = [str(y) for y in selected_years]
    if custom_year.strip():
        all_years_str.append(custom_year.strip())
    if all_years_str:
        filtered_df = filtered_df[filtered_df['year'].astype(str).str.contains('|'.join(all_years_str), case=False, na=False)]
 
    # ===== FILTER SUMMARY =====
    filter_summary = []
    if selected_colleges or custom_college.strip():
        filter_summary.append(f"College: {', '.join(selected_colleges[:2])}{'...' if len(selected_colleges)>2 else ''}{' + custom' if custom_college.strip() else ''}")
    if selected_depts or custom_dept.strip():
        filter_summary.append(f"Dept: {', '.join(selected_depts[:2])}{'...' if len(selected_depts)>2 else ''}{' + custom' if custom_dept.strip() else ''}")
    if selected_years or custom_year.strip():
        filter_summary.append(f"Year: {', '.join(map(str, selected_years[:2]))}{'...' if len(selected_years)>2 else ''}{' + custom' if custom_year.strip() else ''}")
 
    col_summary1, col_summary2 = st.columns([3, 1])
    with col_summary1:
        st.markdown(f"""
        <div class="filter-stats">
            <strong>Showing {len(filtered_df)} of {len(df)} students</strong>
            {' | Filters: ' + ' | '.join(filter_summary) if filter_summary else ''}
        </div>
        """, unsafe_allow_html=True)
    with col_summary2:
        if st.button("Clear All Filters", key="clear_filters_btn"):
            st.session_state['selected_colleges'] = []
            st.session_state['custom_college'] = ''
            st.session_state['selected_depts'] = []
            st.session_state['custom_dept'] = ''
            st.session_state['selected_years'] = []
            st.session_state['custom_year'] = ''
            st.rerun()
 
    if filtered_df.empty:
        st.warning("No students match your filters!")
        st.info("Leave dropdowns empty to show all students, or check your custom text spelling.")
        st.stop()
 
    # Update session state
    st.session_state.selected_colleges = selected_colleges
    st.session_state.custom_college = custom_college
    st.session_state.selected_depts = selected_depts
    st.session_state.custom_dept = custom_dept
    st.session_state.selected_years = selected_years
    st.session_state.custom_year = custom_year
 
    # ============ KPIs, Charts, Table ============

    score_columns_present = any(c in filtered_df.columns for c in ["final_score", "quant_score", "logic_score", "verbal_score"])
 
    if score_columns_present and "final_score" in filtered_df.columns:
        st.markdown("### Key Performance Indicators")
 
        total_students = len(filtered_df)
        avg_quant  = filtered_df['quant_score'].mean()  if 'quant_score'  in filtered_df.columns else 0
        avg_logic  = filtered_df['logic_score'].mean()  if 'logic_score'  in filtered_df.columns else 0
        avg_verbal = filtered_df['verbal_score'].mean() if 'verbal_score' in filtered_df.columns else 0
        avg_final  = filtered_df['final_score'].mean()  if 'final_score'  in filtered_df.columns else 0
        top_final_90 = len(filtered_df[filtered_df['final_score'] >= 75]) if 'final_score' in filtered_df.columns else 0
        top_final    = len(filtered_df[filtered_df['final_score'] >= 45]) if 'final_score' in filtered_df.columns else 0
        top_score    = filtered_df['final_score'].max() if 'final_score' in filtered_df.columns else 0
 
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Students", total_students)
        col2.metric("Avg Quantitative Aptitude Score", f"{avg_quant:.1f} / 5.0")
        col3.metric("Avg Logical Reasoning Score", f"{avg_logic:.1f} / 5.0")
        col4.metric("Avg Verbal Ability Score", f"{avg_verbal:.1f} / 5.0")
 
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Avg Final Score", f"{avg_final:.1f}%")
        col6.metric("Tier A (75%+)", f"{top_final_90}")
        col7.metric("Tier B (45%+)", f"{top_final}")
        col8.metric("#1 Performer's Score", f"{top_score:.1f}%")
 
    # ===== Score Analytics (only if score columns exist) =====
    if "final_score" in filtered_df.columns:
        st.markdown("### Score Analytics")
        row1_col1, row1_col2 = st.columns(2)
 
        with row1_col1:
            college_counts = filtered_df['college_name'].value_counts().head(10).reset_index()
            college_counts.columns = ['College', 'Student Count']
            fig_college = px.bar(college_counts, x='Student Count', y='College',
                                 title="Students per College (Top 10)",
                                 orientation='h', color='Student Count',
                                 color_continuous_scale='Viridis')
            fig_college.update_traces(hovertemplate='%{y}: <b>%{x}</b><extra></extra>')
            fig_college.update_layout(showlegend=False, hovermode='y unified')
            st.plotly_chart(fig_college, width="stretch")
 
        with row1_col2:
            dept_counts = filtered_df['department'].value_counts().head(10).reset_index()
            dept_counts.columns = ['Department', 'Student Count']
            fig_dept = px.bar(dept_counts, x='Student Count', y='Department',
                              title="Students per Department (Top 10)",
                              orientation='h', color='Student Count',
                              color_continuous_scale='Plasma')
            fig_dept.update_traces(hovertemplate='%{y}: <b>%{x}</b><extra></extra>')
            fig_dept.update_layout(showlegend=False, hovermode='y unified')
            st.plotly_chart(fig_dept, width="stretch")
 
        row2_col1, row2_col2 = st.columns(2)
 
        with row2_col1:
            avg_scores = pd.DataFrame({
                'Score Type': ['Quant', 'Logic', 'Verbal'],
                'Average': [
                    filtered_df['quant_score'].mean()  if 'quant_score'  in filtered_df.columns else 0,
                    filtered_df['logic_score'].mean()  if 'logic_score'  in filtered_df.columns else 0,
                    filtered_df['verbal_score'].mean() if 'verbal_score' in filtered_df.columns else 0,
                ]
            })
            fig_avg = px.bar(avg_scores, x='Score Type', y='Average',
                             title="Average Scores Comparison",
                             color='Average', color_continuous_scale='Viridis')
            fig_avg.update_traces(hovertemplate='%{x}: <b>%{y:.1f}</b><extra></extra>')
            fig_avg.update_layout(showlegend=False, hovermode='x unified')
            st.plotly_chart(fig_avg, width="stretch")
 
        with row2_col2:
            if 'year' in filtered_df.columns and not filtered_df.empty:
                year_avg = filtered_df.groupby('year')['final_score'].mean().reset_index()
                year_avg['year'] = year_avg['year'].astype(str)
                fig_year = px.bar(year_avg, x='year', y='final_score',
                                  title="Average Final Score by Year",
                                  color='final_score', color_continuous_scale='Viridis')
            else:
                st.info("Year column not found; skipping Average Final Score by Year")
                fig_year = px.bar(title="Average Final Score by Year (No Data)")
            fig_year.update_traces(hovertemplate='%{x}: <b>%{y:.1f}</b><extra></extra>')
            fig_year.update_layout(showlegend=False, hovermode='x unified')
            st.plotly_chart(fig_year, width="stretch")
 
        st.markdown("### Top 10 Performers (Final Score)")
        top_students = filtered_df.nlargest(10, 'final_score')[[
            'quant_score'  if 'quant_score'  in filtered_df.columns else filtered_df.columns[0],
            'logic_score'  if 'logic_score'  in filtered_df.columns else filtered_df.columns[0],
            'verbal_score' if 'verbal_score' in filtered_df.columns else filtered_df.columns[0],
            'final_score',
        ]]
        top_students = top_students.loc[:, ~top_students.columns.duplicated()]
        st.dataframe(top_students, width="stretch")
 
        st.markdown("---")
        st.markdown("### Student Scores Table")
    else:
        st.info("Score Analytics skipped: loaded dataset has no final_score column.")
        st.markdown("### Student Scores Table")
 
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        if 'student_id' in df.columns:
            df['student_id'] = df['student_id'].fillna('').astype(str)
            student_ids = sorted(df['student_id'].drop_duplicates().dropna().unique().tolist())
        else:
            student_ids = []
            st.warning("No student_id column found in data - student filter disabled")
 
        if student_ids:
            def _format_student_id(x):
                s = str(x).strip()
                if len(s) <= 8:
                    return s
                return s[:8] + "..." + s[-4:]
 
            student_id = st.selectbox(
                "Filter by Student ID",
                options=student_ids,
                index=0,
                format_func=_format_student_id,
            )
        else:
            student_id = None
 
    with search_col2:
        csv = filtered_df.reset_index().to_csv(index=False)
        st.download_button(
            label="Export CSV",
            data=csv,
            file_name=f"classifications_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
 
    if st.checkbox("Show specific student data") and student_id:
        if 'student_id' in filtered_df.columns:
            filtered_df = filtered_df.copy()
            filtered_df['student_id'] = filtered_df['student_id'].fillna('').astype(str)
            st.dataframe(filtered_df[filtered_df['student_id'] == str(student_id)])
        else:
            st.warning("Student ID not found or no student_id column")
    else:
        with st.expander("View All Filtered Data", expanded=False):
            st.markdown(
                """
                <div class="filter-column" style="padding: 0.75rem; background: rgba(15,23,42,0.80) !important;">
                """,
                unsafe_allow_html=True,
            )
            st.dataframe(filtered_df.reset_index(), width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)
 
    st.caption(f"Auto-refreshes every {REFRESH_SECONDS}s | Student ID is unique identifier")
 
 
def init_session_state():
    """
    Initialize session state for categorical filters only.
    """
    
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