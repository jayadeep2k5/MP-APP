import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Hospital Community Outreach Dashboard")

# ---------------- LOAD DATA SAFELY ----------------
try:
    df = pd.read_excel("Hospital_Free_Services_Dataset.xlsx")
    st.success("✅ Data Loaded Successfully")
except Exception as e:
    st.error(f"❌ Error loading file: {e}")
    st.stop()

# ---------------- DEBUG (REMOVE LATER) ----------------
st.write("Columns in dataset:", df.columns)

# ---------------- COLUMN MAPPING (IMPORTANT) ----------------
# Adjust automatically if names slightly differ
def find_col(possible_names):
    for col in df.columns:
        for name in possible_names:
            if name.lower() in col.lower():
                return col
    return None

patient_col = find_col(["patient id", "patient"])
cost_col = find_col(["cost", "service cost"])
dept_col = find_col(["department"])
month_col = find_col(["month"])
income_col = find_col(["income"])
outcome_col = find_col(["outcome"])
age_col = find_col(["age"])
district_col = find_col(["district", "location"])

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Filters")

if dept_col:
    dept_filter = st.sidebar.multiselect("Department", df[dept_col].dropna().unique(), default=df[dept_col].dropna().unique())
    df = df[df[dept_col].isin(dept_filter)]

if month_col:
    month_filter = st.sidebar.multiselect("Month", df[month_col].dropna().unique(), default=df[month_col].dropna().unique())
    df = df[df[month_col].isin(month_filter)]

if income_col:
    income_filter = st.sidebar.multiselect("Income Group", df[income_col].dropna().unique(), default=df[income_col].dropna().unique())
    df = df[df[income_col].isin(income_filter)]

st.write("Filtered rows:", len(df))

# ---------------- KPI CALCULATIONS ----------------
try:
    total_patients = df[patient_col].nunique() if patient_col else len(df)
    total_value = df[cost_col].sum() if cost_col else 0

    recovery_rate = (
        (df[outcome_col].str.contains("recover", case=False, na=False)).sum()
        / len(df) * 100
    ) if outcome_col else 0

    avg_cost = total_value / total_patients if total_patients else 0
except:
    st.error("⚠️ Issue in KPI calculation")
    st.stop()

# ---------------- KPI CARDS ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Patients Served", total_patients)
col2.metric("Financial Impact (₹)", f"{total_value:,.0f}")
col3.metric("Recovery Rate", f"{recovery_rate:.1f}%")
col4.metric("Avg Cost / Patient", f"₹{avg_cost:,.0f}")

# ---------------- CHARTS ----------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("Monthly Patients")

    if month_col and patient_col:
        monthly = df.groupby(month_col)[patient_col].count().reset_index()
        fig = px.bar(monthly, x=month_col, y=patient_col)
        st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Department Distribution")

    if dept_col:
        dept_data = df[dept_col].value_counts().reset_index()
        dept_data.columns = ["Department", "Count"]
        fig2 = px.pie(dept_data, names="Department", values="Count", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

# ---------------- SECOND ROW ----------------
col7, col8, col9 = st.columns(3)

with col7:
    st.subheader("Location")

    if district_col:
        loc = df[district_col].value_counts().reset_index()
        loc.columns = ["Location", "Count"]
        fig3 = px.bar(loc, x="Location", y="Count")
        st.plotly_chart(fig3, use_container_width=True)

with col8:
    st.subheader("Age Distribution")

    if age_col:
        fig4 = px.histogram(df, x=age_col, nbins=5)
        st.plotly_chart(fig4, use_container_width=True)

with col9:
    st.subheader("Health Outcomes")

    if outcome_col:
        outcome = df[outcome_col].value_counts().reset_index()
        outcome.columns = ["Outcome", "Count"]
        fig5 = px.bar(outcome, x="Outcome", y="Count", color="Outcome")
        st.plotly_chart(fig5, use_container_width=True)