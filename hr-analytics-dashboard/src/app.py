import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px

# Import local modules
from data_loader import load_sample_data, calculate_metrics
import visualizations as viz

# Page configuration
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {font-size:24px; font-weight:bold; color:#1f77b4; margin-bottom:20px;}
    .metric-card {background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 20px;}
    .metric-value {font-size: 28px; font-weight: bold; color: #1f77b4;}
    .metric-label {font-size: 14px; color: #6c757d;}
    .section-header {border-bottom: 2px solid #dee2e6; padding-bottom: 10px; margin-top: 30px;}
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return load_sample_data()

df = load_data()
metrics = calculate_metrics(df)

# Sidebar
st.sidebar.title("Filters")
st.sidebar.markdown("### Department")
departments = ['All'] + sorted(df['department'].unique().tolist())
selected_departments = st.sidebar.multiselect(
    'Select Departments', 
    options=departments[1:], 
    default=departments[1:],
    key='dept_filter'
)

# Apply filters
if 'All' in selected_departments or not selected_departments:
    filtered_df = df
else:
    filtered_df = df[df['department'].isin(selected_departments)]

# Main content
st.title("HR Analytics Dashboard")
st.markdown("---")

# Key Metrics
st.markdown("### Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='metric-card'>"
                f"<div class='metric-value'>{len(filtered_df):,}</div>"
                "<div class='metric-label'>Total Employees</div>"
                "</div>", unsafe_allow_html=True)

with col2:
    attrition_rate = filtered_df['attrition'].mean() * 100
    st.markdown("<div class='metric-card'>"
                f"<div class='metric-value'>{attrition_rate:.1f}%</div>"
                "<div class='metric-label'>Attrition Rate</div>"
                "</div>", unsafe_allow_html=True)

with col3:
    avg_salary = filtered_df['salary'].mean()
    st.markdown("<div class='metric-card'>"
                f"<div class='metric-value'>${avg_salary:,.0f}</div>"
                "<div class='metric-label'>Avg. Salary</div>"
                "</div>", unsafe_allow_html=True)

with col4:
    avg_satisfaction = filtered_df['satisfaction'].mean()
    st.markdown("<div class='metric-card'>"
                f"<div class='metric-value'>{avg_satisfaction:.1f}/5.0</div>"
                "<div class='metric-label'>Avg. Satisfaction</div>"
                "</div>", unsafe_allow_html=True)

# First row of charts
st.markdown("<div class='section-header'></div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(viz.create_attrition_chart(filtered_df), use_container_width=True)

with col2:
    st.plotly_chart(viz.create_department_metrics(filtered_df), use_container_width=True)

# Second row of charts
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(viz.create_salary_distribution(filtered_df), use_container_width=True)

with col2:
    st.plotly_chart(viz.create_tenure_vs_satisfaction(filtered_df), use_container_width=True)

# Third row - Demographic Analysis
st.markdown("<h3 class='section-header'>Demographic Analysis</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

age_fig, gender_fig = viz.create_demographic_metrics(filtered_df)
with col1:
    st.plotly_chart(age_fig, use_container_width=True)

with col2:
    st.plotly_chart(gender_fig, use_container_width=True)

# Fourth row - Attrition Analysis
st.markdown("<h3 class='section-header'>Attrition Analysis</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

dept_fig, pos_fig = viz.create_attrition_analysis(filtered_df)
with col1:
    st.plotly_chart(dept_fig, use_container_width=True)

with col2:
    st.plotly_chart(pos_fig, use_container_width=True)

# Add some space at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)

# Add a button to show raw data
if st.sidebar.checkbox('Show raw data'):
    st.subheader('Raw Data')
    st.dataframe(filtered_df)

# Add a download button for the filtered data
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(filtered_df)
st.sidebar.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='hr_analytics_data.csv',
    mime='text/csv',
)

# Add a footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This HR Analytics Dashboard provides insights into employee data, "
    "helping HR professionals make data-driven decisions."
)
st.sidebar.markdown("---")
st.sidebar.markdown("© 2023 HR Analytics Dashboard")
