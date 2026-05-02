import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from constants import REFRESH_SECONDS

# ============= FILTERS SECTION =============
def filter_data(df):
    st.markdown("### 🔍 Interactive Filters")

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        # Department filter
        all_depts = ["All Departments"] + sorted(df['Department/Class'].dropna().unique().tolist())
        selected_dept = st.selectbox("Department", all_depts)

    with filter_col2:
        # Semester filter
        all_sems = ["All Semesters"] + sorted(df['Semster/Section'].dropna().unique().tolist())
        selected_sem = st.selectbox("Semester", all_sems)

    with filter_col3:
        # Course filter
        all_courses = ["All Courses"] + sorted(df['Course'].dropna().unique().tolist())
        selected_course = st.selectbox("Course", all_courses)

    with filter_col4:
        # College filter
        all_colleges = ["All Colleges"] + sorted(df['College Name/ School Name'].dropna().unique().tolist())
        selected_college = st.selectbox("College", all_colleges)

    # Apply filters
    filtered_df = df.copy()
    if selected_dept != "All Departments":
        filtered_df = filtered_df[filtered_df['Department/Class'] == selected_dept]
    if selected_sem != "All Semesters":
        filtered_df = filtered_df[filtered_df['Semster/Section'] == selected_sem]
    if selected_course != "All Courses":
        filtered_df = filtered_df[filtered_df['Course'] == selected_course]
    if selected_college != "All Colleges":
        filtered_df = filtered_df[filtered_df['College Name/ School Name'] == selected_college]

    # Show filter stats
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} records**")

    if filtered_df.empty:
        st.warning("No records match your filters")
    else:
        # ============ KPI SECTION ============
        st.markdown("### 🎯 Key Performance Indicators")
        
        # Calculate KPI values
        total_responses = len(filtered_df)
        total_students = filtered_df['Full Name'].nunique()
        total_hours = filtered_df['Hours spent'].sum()
        avg_hours = filtered_df['Hours spent'].mean()
        total_colleges = filtered_df['College Name/ School Name'].nunique()
        total_departments = filtered_df['Department/Class'].nunique()
        total_courses = filtered_df['Course'].nunique()
        
        # Display KPI metrics in rows
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📝 Total Responses", total_responses)
        col2.metric("👥 Unique Students", total_students)
        col3.metric("⏱️ Total Hours Spent", f"{total_hours:,.0f}")
        col4.metric("📚 Average Hours/Student", f"{avg_hours:.1f}")
        
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("🏛️ Colleges", total_colleges)
        col6.metric("📋 Departments", total_departments)
        col7.metric("🎓 Courses", total_courses)
        col8.metric("📅 Latest Enrollment", filtered_df['Date of Enrollment'].max().strftime('%d %b %Y') if pd.notna(filtered_df['Date of Enrollment'].max()) else "N/A")
        
        st.markdown("---")
        
        # ============ VISUALIZATIONS SECTION ============
    st.markdown("### 📈 Visualizations")
    
    # Row 1: Distribution charts
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("#### Students by Department")
        dept_counts = filtered_df['Department/Class'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Count']
        fig_dept = px.bar(dept_counts, x='Department', y='Count', 
                        color='Count', color_continuous_scale='Blues',
                        title="Student Distribution by Department")
        fig_dept.update_layout(showlegend=False)
        st.plotly_chart(fig_dept, width='stretch')
    
    with row1_col2:
        st.markdown("#### Students by College")
        college_counts = filtered_df['College Name/ School Name'].value_counts().reset_index()
        college_counts.columns = ['College', 'Count']
        fig_college = px.bar(college_counts, x='College', y='Count',
                           color='Count', color_continuous_scale='Greens',
                           title="Student Distribution by College")
        fig_college.update_layout(showlegend=False)
        st.plotly_chart(fig_college, width='stretch')
    
    # Row 2: Course and Semester charts
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown("#### Students by Course")
        course_counts = filtered_df['Course'].value_counts().reset_index()
        course_counts.columns = ['Course', 'Count']
        fig_course = px.bar(course_counts, x='Course', y='Count',
                         color='Count', color_continuous_scale='Purples',
                         title="Student Distribution by Course")
        fig_course.update_layout(showlegend=False)
        st.plotly_chart(fig_course, width='stretch')
    
    with row2_col2:
        st.markdown("#### Students by Semester")
        semester_counts = filtered_df['Semster/Section'].value_counts().reset_index()
        semester_counts.columns = ['Semester', 'Count']
        fig_semester = px.pie(semester_counts, values='Count', names='Semester',
                           title="Distribution by Semester/Section",
                           color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_semester, width='stretch')
    
    # Row 3: Hours analysis
    row3_col1, row3_col2 = st.columns(2)
    
    with row3_col1:
        st.markdown("#### Hours Spent by Course (Average)")
        avg_hours_course = filtered_df.groupby('Course')['Hours spent'].mean().reset_index()
        avg_hours_course.columns = ['Course', 'Avg Hours']
        avg_hours_course = avg_hours_course.sort_values('Avg Hours', ascending=False)
        fig_hours_course = px.bar(avg_hours_course, x='Course', y='Avg Hours',
                                color='Avg Hours', color_continuous_scale='Oranges',
                                title="Average Hours Spent by Course")
        fig_hours_course.update_layout(showlegend=False)
        st.plotly_chart(fig_hours_course, width='stretch')
    
    with row3_col2:
        st.markdown("#### Hours Distribution")
        fig_hours_hist = px.histogram(filtered_df, x='Hours spent', 
                                   nbins=20,
                                   title="Distribution of Hours Spent",
                                   color_discrete_sequence=['#636EFA'])
        fig_hours_hist.update_layout(showlegend=False, yaxis_title="Count")
        st.plotly_chart(fig_hours_hist, width='stretch')
    
    # Row 4: Enrollment trend
    st.markdown("#### Enrollment Trend Over Time")
    
    # Group by month
    filtered_df = filtered_df.copy()
    filtered_df['Month'] = filtered_df['Date of Enrollment'].dt.to_period('M')
    enrollment_trend = filtered_df.groupby('Month').size().reset_index()
    enrollment_trend['Month'] = enrollment_trend['Month'].astype(str)
    enrollment_trend.columns = ['Month', 'Count']
    
    fig_trend = px.line(enrollment_trend, x='Month', y='Count',
                      title="Enrollment Trend",
                      markers=True,
                      color_discrete_sequence=['#00CC96'])
    st.plotly_chart(fig_trend, width='stretch')
    
    st.markdown("---")
    
    # ============ DATA TABLE SECTION ============
    st.markdown("### 📋 Data Table")
    
    # Search functionality
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_term = st.text_input("🔍 Search records", placeholder="Search by name, college, department...")
    with search_col2:
        # Export button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"placed_dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Apply search filter
    if search_term:
        search_filter = (
            filtered_df['Full Name'].str.contains(search_term, case=False, na=False) |
            filtered_df['College Name/ School Name'].str.contains(search_term, case=False, na=False) |
            filtered_df['Department/Class'].str.contains(search_term, case=False, na=False) |
            filtered_df['Course'].str.contains(search_term, case=False, na=False)
        )
        display_df = filtered_df[search_filter]
        st.markdown(f"**Found {len(display_df)} matching records**")
    else:
        display_df = filtered_df
    
    # Display table with pagination
    with st.expander("📋 View Raw Data", expanded=False):
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True
        )
    
# ============ AUTO REFRESH (Improved) ============
    # Using Streamlit's native caching - data auto-refreshes based on ttl
    # The manual refresh button above provides user control
    # Display refresh info
    st.caption(f"💡 Data automatically refreshes every {REFRESH_SECONDS} seconds. Use the refresh button for immediate update.")