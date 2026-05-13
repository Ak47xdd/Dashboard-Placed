import streamlit as st
import pandas as pd
import plotly.express as px

from college_dept_map import COLLEGE_VARIANT_CANONICAL_MAP, DEPARTMENT_VARIANT_CANONICAL_MAP


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
    "quant_Q1",
    "quant_Q2",
    "quant_Q3",
    "quant_Q4",
    "quant_Q5",
    "logic_Q1",
    "logic_Q2",
    "logic_Q3",
    "logic_Q4",
    "logic_Q5",
    "verbal_Q1",
    "verbal_Q2",
    "verbal_Q3",
    "verbal_Q4",
    "verbal_Q5",
    "behave_Q1",
    "behave_Q2",
    "behave_Q3",
    "behave_Q4",
    "behave_Q5",
    "commit_Q3",
]


def _normalize_college_and_department(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize spelling variants using canonical maps so filters/charts align."""
    out = df.copy()

    if "college_name" in out.columns and COLLEGE_VARIANT_CANONICAL_MAP:
        s = out["college_name"].fillna("").astype(str).str.strip()
        cn_map = {k.lower(): v for k, v in COLLEGE_VARIANT_CANONICAL_MAP.items()}
        s_lower = s.str.lower()
        for wrong_lower, canonical in cn_map.items():
            mask = s_lower.eq(wrong_lower)
            if mask.any():
                s.loc[mask] = canonical
        out["college_name"] = s

    if "department" in out.columns and DEPARTMENT_VARIANT_CANONICAL_MAP:
        s = out["department"].fillna("").astype(str).str.strip()
        dn_map = {k.lower(): v for k, v in DEPARTMENT_VARIANT_CANONICAL_MAP.items()}
        s_lower = s.str.lower()
        for wrong_lower, canonical in dn_map.items():
            mask = s_lower.eq(wrong_lower)
            if mask.any():
                s.loc[mask] = canonical
        out["department"] = s

    return out


def _safe_value_counts(series: pd.Series) -> pd.DataFrame:
    vc = series.dropna().astype(str).value_counts()
    if vc.empty:
        return pd.DataFrame(columns=["value", "count"])
    return vc.reset_index().rename(columns={"index": "value", series.name: "value"})


def render_student_tab(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        st.info("No student data available.")
        return

    df = _normalize_college_and_department(df)

    # Data volume warning
    if len(df) < 20:
        st.warning(
            f"⚠️ Only {len(df)} students in the dataset. "
            "Distributions are not stable yet — patterns will be meaningful once n ≥ 50."
        )

    # KPI row
    required_id_cols = ["college_name", "department", "career_goal"]
    for c in required_id_cols:
        if c not in df.columns:
            # KPI will still render with partial data
            pass

    placement_pct = 0.0
    if "career_goal" in df.columns:
        # Heuristic: treat career_goal containing 'placement' as placement seekers
        placement_mask = df["career_goal"].astype(str).str.lower().str.contains("placement")
        placement_pct = placement_mask.mean() * 100

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👥 Total Students", len(df))
    k2.metric("🏫 Colleges", df["college_name"].nunique() if "college_name" in df.columns else "-")
    k3.metric("📚 Departments", df["department"].nunique() if "department" in df.columns else "-")
    k4.metric("🎯 In-Campus Placement Seekers", f"{placement_pct:.0f}%")

    st.markdown("---")

    # ===== Section 1 — Who Are They? =====
    st.subheader("Student Demographics & Background")

    col1, col2 = st.columns([2, 1])

    with col1:
        if all(c in df.columns for c in ["college_name", "department", "year"]):
            sun = px.sunburst(
                df,
                path=["college_name", "department", "year"],
                color="year" if "year" in df.columns else None,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            sun.update_layout(title="College → Department → Year Distribution")
            st.plotly_chart(sun, width="stretch")

        else:
            st.info("Missing college_name / department / year columns for sunburst.")

    with col2:
        if "medium" in df.columns:
            medium_counts = (
                df["medium"].dropna().astype(str).value_counts().reset_index()
            )
            medium_counts.columns = ["medium", "count"]
            donut = px.pie(
                medium_counts,
                names="medium",
                values="count",
                hole=0.45,
            )
            donut.update_layout(title="Medium of Instruction")
            st.plotly_chart(donut, width="stretch")
        else:
            st.info("Missing medium column for donut.")

    # ===== Section 2 — Goals & Readiness =====
    st.subheader("Goals & Readiness")
    col1, col2 = st.columns([1, 1])

    with col1:
        if all(c in df.columns for c in ["career_goal", "have_prep_test"]):
            tmp = df[["career_goal", "have_prep_test"]].dropna().copy()
            tmp["career_goal"] = tmp["career_goal"].astype(str).str.strip()
            tmp["have_prep_test"] = tmp["have_prep_test"].astype(str).str.strip()

            fig = px.bar(
                tmp,
                y="career_goal",
                color="have_prep_test",
                orientation="h",
                barmode="group",
                title="Career Goal × Prep Test Status",
            )
            fig.update_layout(yaxis_title="Career Goal", xaxis_title="Number of Students")
            st.plotly_chart(fig, width="stretch")

        else:
            st.info("Missing career_goal and/or have_prep_test columns.")

    with col2:
        if "career_goal" in df.columns:
            cg_counts = df["career_goal"].dropna().astype(str).value_counts().reset_index()
            cg_counts.columns = ["career_goal", "count"]
            fig = px.pie(cg_counts, names="career_goal", values="count", hole=0.45)
            fig.update_layout(title="Career Goal × Prep Test Status")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Missing career_goal column.")

    # ===== Section 3 — Learning Profile =====
    st.subheader("Learning Profile")

    # Exclude zero-variance columns
    dims_all = ["learn_Q1", "learn_Q2", "learn_Q3", "learn_Q4"]
    instr_all = ["instruct_Q1", "instruct_Q2", "instruct_Q3", "instruct_Q4", "instruct_Q5", "instruct_Q6"]
    content_all = ["content_pref_Q1", "content_pref_Q2", "content_pref_Q3"]
    engage_all = ["engage_Q1", "engage_Q2", "engage_Q3", "engage_Q4"]

    learn_dims = [c for c in dims_all if c in df.columns and c not in ZERO_VARIANCE_COLS]
    # idea.md uses learn_Q1 only; keep it but also allow learn_Q2 if present.
    # We will build flow as: learn_Q1 (prefer), instruct_Q1, content_pref_Q1, engage_Q1
    flow_dims = [
        "learn_Q1" if "learn_Q1" in df.columns else None,
        "instruct_Q1" if "instruct_Q1" in df.columns else None,
        "content_pref_Q1" if "content_pref_Q1" in df.columns else None,
        "engage_Q1" if "engage_Q1" in df.columns else None,
    ]
    flow_dims = [d for d in flow_dims if d is not None and d not in ZERO_VARIANCE_COLS]

    if len(flow_dims) >= 3:
        # parallel_categories expects at least 2 dimensions
        color_col = "career_goal" if "career_goal" in df.columns else None
        tmp = df[flow_dims + ([color_col] if color_col else [])].dropna().copy()
        if not tmp.empty:
            tmp[color_col] = tmp[color_col].astype(str)
            # Using codes like idea.md, but only if we have a color column.
            color_codes = tmp[color_col].astype("category").cat.codes if color_col else None

            fig_pc = px.parallel_categories(
                tmp,
                dimensions=flow_dims,
                color=color_codes,
                color_continuous_scale=px.colors.sequential.Inferno,
            )
            fig_pc.update_layout(title="Learning Profile Flow")
            st.plotly_chart(fig_pc, width="stretch")

    # Heatmap: question × response frequency (as %)
    heat_questions = [
        "learn_Q1",
        "learn_Q2",
        "instruct_Q1",
        "instruct_Q5",
        "instruct_Q6",
        "content_pref_Q1",
        "engage_Q1",
        "engage_Q2",
        "commit_Q2",
    ]
    heat_questions = [q for q in heat_questions if q in df.columns and q not in ZERO_VARIANCE_COLS]

    if heat_questions:
        matrix = []
        col_labels = []
        for q in heat_questions:
            vc = df[q].dropna().astype(str).value_counts(normalize=True)
            if vc.empty:
                continue
            # Make a consistent column set across questions
            for opt in vc.index.tolist():
                if opt not in col_labels:
                    col_labels.append(opt)
        # Build matrix in col_labels order
        for q in heat_questions:
            vc = df[q].dropna().astype(str).value_counts(normalize=True)
            row = [float(vc.get(opt, 0.0)) * 100 for opt in col_labels]
            matrix.append(row)

        if matrix:
            fig_hm = px.imshow(
                matrix,
                x=col_labels,
                y=heat_questions,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="YlOrRd",
                labels={"x": "Response Option", "y": "Question", "color": "% of Students"},
            )
            fig_hm.update_layout(title="Response Frequency Heatmap", height=400)
            st.plotly_chart(fig_hm, width="stretch")

    st.markdown("---")

    # ===== Section 4 — Engagement & Commitment =====
    st.subheader("Engagement & Commitment")

    col1, col2 = st.columns([1, 1])

    with col1:
        if "engage_Q3" in df.columns and "engage_Q3" not in ZERO_VARIANCE_COLS:
            counts = df["engage_Q3"].dropna().astype(str).value_counts().reset_index()
            counts.columns = ["engage_Q3", "count"]
            fig = px.bar(
                counts,
                x="count",
                y="engage_Q3",
                orientation="h",
                color="count",
                color_continuous_scale="Viridis",
                title="What Motivates Engagement (engage_Q3)",
            )
            fig.update_layout(yaxis_title="Engagement Factor", xaxis_title="Number of Students")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Missing engage_Q3 column.")

    with col2:
        if "commit_Q2" in df.columns and "commit_Q2" not in ZERO_VARIANCE_COLS:
            counts = df["commit_Q2"].dropna().astype(str).value_counts().reset_index()
            counts.columns = ["commit_Q2", "count"]
            fig = px.pie(counts, names="commit_Q2", values="count", hole=0.45)
            fig.update_layout(title="Barriers to Commitment")
            st.plotly_chart(fig, width="stretch")

        else:
            st.info("Missing commit_Q2 column.")

    if all(c in df.columns for c in ["engage_Q1", "engage_Q4"]):
        tmp = df[["engage_Q1", "engage_Q4"]].dropna().copy()
        if not tmp.empty:
            fig_stack = px.bar(tmp, x="engage_Q1", color="engage_Q4", barmode="stack")
            fig_stack.update_layout(title="Engagement Frequency × Prep Test Status")
            st.plotly_chart(fig_stack, width="stretch")

    # ===== Data table (Raw STUDENT_DATA) =====
    st.subheader("Student Responses (Filtered)")

    # Remove zero-variance columns and score-related columns (scores only exist in classification view)
    cols_to_drop = set(DF_COLS_TO_DROP)
    score_cols = {
        "quant_score",
        "logic_score",
        "verbal_score",
        "final_score",
        "created_at",
    }
    cols_to_drop |= score_cols

    table_df = df.copy()
    existing_drop = [c for c in cols_to_drop if c in table_df.columns]
    if existing_drop:
        table_df = table_df.drop(columns=existing_drop)

    # Put identity columns first if present
    identity_order = [
        "student_id",
        "student_name",
        "college_name",
        "department",
        "course_type",
        "year",
        "medium",
    ]
    ordered = [c for c in identity_order if c in table_df.columns]
    rest = [c for c in table_df.columns if c not in ordered]
    table_df = table_df[ordered + rest]

    # ===== Search / Filter table (Student ID) =====

    if "student_id" in df.columns:
        table_df_for_search = table_df.copy()
        table_df_for_search["student_id"] = table_df_for_search["student_id"].fillna("").astype(str)
        student_ids = sorted(table_df_for_search["student_id"].drop_duplicates().dropna().unique().tolist())

        if student_ids:
            def _format_student_id(x):
                s = str(x).strip()
                if len(s) <= 8:
                    return s
                return s[:8] + "..." + s[-4:]

            search_col1, search_col2 = st.columns([4, 1])
            with search_col1:
                selected_student_id = st.selectbox(
                    "🔍 Filter by Student ID",
                    options=student_ids,
                    index=0,
                    format_func=_format_student_id,
                )
            with search_col2:
                show_expander = st.checkbox("👤 Show", value=True)

            if show_expander:
                st.dataframe(
                    table_df_for_search[table_df_for_search["student_id"] == str(selected_student_id)].reset_index(
                        drop=True
                    ),
                    width="stretch",
                )
            else:
                st.dataframe(table_df_for_search.reset_index(drop=True), width="stretch")
        else:
            st.dataframe(table_df.reset_index(drop=True), width="stretch")
    else:
        st.dataframe(table_df.reset_index(drop=True), width="stretch")
