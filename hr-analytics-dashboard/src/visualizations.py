import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd

def create_attrition_chart(df):
    """Create a pie chart showing attrition distribution."""
    attrition_count = df['attrition'].value_counts().reset_index()
    attrition_count.columns = ['Attrition', 'Count']
    
    fig = px.pie(
        attrition_count, 
        values='Count', 
        names=attrition_count['Attrition'].map({0: 'Active', 1: 'Attrited'}),
        title='Employee Attrition Distribution',
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=20, l=0, r=0)
    )
    return fig

def create_department_metrics(df):
    """Create a bar chart showing employee count by department."""
    dept_counts = df['department'].value_counts().reset_index()
    dept_counts.columns = ['Department', 'Employee Count']
    
    fig = px.bar(
        dept_counts, 
        x='Department', 
        y='Employee Count',
        title='Employee Distribution by Department',
        color='Department',
        text='Employee Count'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Number of Employees",
        showlegend=False,
        margin=dict(t=50, b=20, l=0, r=0)
    )
    return fig

def create_salary_distribution(df):
    """Create a histogram of salary distribution."""
    fig = px.histogram(
        df, 
        x='salary', 
        nbins=20,
        title='Salary Distribution',
        labels={'salary': 'Annual Salary ($)'},
        color_discrete_sequence=['#636EFA']
    )
    fig.update_layout(
        xaxis_title="Annual Salary ($)",
        yaxis_title="Number of Employees",
        margin=dict(t=50, b=20, l=0, r=0)
    )
    return fig

def create_tenure_vs_satisfaction(df):
    """Create a scatter plot of tenure vs satisfaction."""
    fig = px.scatter(
        df, 
        x='tenure', 
        y='satisfaction',
        color='attrition',
        title='Tenure vs Job Satisfaction',
        labels={
            'tenure': 'Tenure (Years)',
            'satisfaction': 'Job Satisfaction (1-5)',
            'attrition': 'Attrition Status'
        },
        color_discrete_map={0: '#636EFA', 1: '#EF553B'}
    )
    fig.update_layout(
        legend_title_text='',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=20, l=0, r=0)
    )
    return fig

def create_demographic_metrics(df):
    """Create demographic metrics visualizations."""
    # Age distribution
    age_fig = px.histogram(
        df, 
        x='age', 
        nbins=15,
        title='Age Distribution',
        labels={'age': 'Age'},
        color_discrete_sequence=['#00CC96']
    )
    age_fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Number of Employees",
        margin=dict(t=50, b=20, l=0, r=0)
    )
    
    # Gender distribution
    gender_fig = px.pie(
        df, 
        names='gender', 
        title='Gender Distribution',
        hole=0.6
    )
    gender_fig.update_traces(textposition='inside', textinfo='percent+label')
    gender_fig.update_layout(
        showlegend=False,
        margin=dict(t=50, b=20, l=0, r=0)
    )
    
    return age_fig, gender_fig

def create_attrition_analysis(df):
    """Create visualizations for attrition analysis."""
    # Attrition by department
    dept_attrition = df.groupby(['department', 'attrition']).size().unstack().fillna(0)
    dept_attrition['attrition_rate'] = (dept_attrition[1] / (dept_attrition[0] + dept_attrition[1])) * 100
    dept_attrition = dept_attrition.reset_index()
    
    dept_fig = px.bar(
        dept_attrition, 
        x='department', 
        y='attrition_rate',
        title='Attrition Rate by Department',
        text_auto='.1f',
        labels={'attrition_rate': 'Attrition Rate (%)', 'department': 'Department'}
    )
    dept_fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    dept_fig.update_layout(
        yaxis_title="Attrition Rate (%)",
        xaxis_title="",
        margin=dict(t=50, b=20, l=0, r=0)
    )
    
    # Attrition by position
    pos_attrition = df.groupby(['position', 'attrition']).size().unstack().fillna(0)
    pos_attrition['attrition_rate'] = (pos_attrition[1] / (pos_attrition[0] + pos_attrition[1])) * 100
    pos_attrition = pos_attrition.reset_index()
    
    pos_fig = px.bar(
        pos_attrition, 
        x='position', 
        y='attrition_rate',
        title='Attrition Rate by Position',
        text_auto='.1f',
        labels={'attrition_rate': 'Attrition Rate (%)', 'position': 'Position'}
    )
    pos_fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    pos_fig.update_layout(
        yaxis_title="Attrition Rate (%)",
        xaxis_title="",
        margin=dict(t=50, b=20, l=0, r=0)
    )
    
    return dept_fig, pos_fig
