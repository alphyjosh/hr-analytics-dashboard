import pandas as pd
import numpy as np
from pathlib import Path

def load_sample_data():
    """
    Generate and return sample HR data for demonstration purposes.
    Returns a pandas DataFrame with sample HR metrics.
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate sample data
    n_employees = 100
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance']
    positions = ['Manager', 'Senior', 'Mid-level', 'Junior', 'Intern']
    education = ["Bachelor's", "Master's", 'PhD', 'High School']
    
    data = {
        'employee_id': range(1, n_employees + 1),
        'department': np.random.choice(departments, n_employees, p=[0.3, 0.2, 0.25, 0.1, 0.15]),
        'position': np.random.choice(positions, n_employees, p=[0.1, 0.2, 0.4, 0.2, 0.1]),
        'age': np.random.normal(35, 8, n_employees).astype(int).clip(22, 65),
        'tenure': np.random.gamma(3, 1, n_employees).astype(int).clip(0, 15),
        'salary': np.random.normal(75000, 25000, n_employees).astype(int).clip(30000, 200000),
        'education': np.random.choice(education, n_employees, p=[0.4, 0.45, 0.05, 0.1]),
        'gender': np.random.choice(['Male', 'Female', 'Other'], n_employees, p=[0.52, 0.45, 0.03]),
        'attrition': np.random.choice([0, 1], n_employees, p=[0.85, 0.15]),
        'satisfaction': np.random.randint(1, 6, n_employees),
        'performance_rating': np.random.randint(1, 6, n_employees),
        'work_life_balance': np.random.randint(1, 6, n_employees),
        'overtime': np.random.choice([0, 1], n_employees, p=[0.7, 0.3])
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some date fields
    end_date = pd.Timestamp.now()
    start_dates = [end_date - pd.Timedelta(days=int(365.25 * t)) for t in df['tenure']]
    df['hire_date'] = start_dates
    
    return df

def calculate_metrics(df):
    """
    Calculate key HR metrics from the dataset.
    
    Args:
        df (pd.DataFrame): Input HR data
        
    Returns:
        dict: Dictionary containing calculated metrics
    """
    metrics = {}
    
    # Overall metrics
    metrics['total_employees'] = len(df)
    metrics['attrition_rate'] = df['attrition'].mean() * 100
    metrics['avg_satisfaction'] = df['satisfaction'].mean()
    metrics['avg_tenure'] = df['tenure'].mean()
    
    # Department-wise metrics
    dept_metrics = df.groupby('department').agg({
        'employee_id': 'count',
        'attrition': 'mean',
        'salary': 'mean',
        'satisfaction': 'mean'
    }).rename(columns={
        'employee_id': 'employee_count',
        'attrition': 'attrition_rate',
        'salary': 'avg_salary',
        'satisfaction': 'avg_satisfaction'
    })
    
    # Position-wise metrics
    position_metrics = df.groupby('position').agg({
        'employee_id': 'count',
        'attrition': 'mean',
        'salary': 'mean'
    }).rename(columns={
        'employee_id': 'employee_count',
        'attrition': 'attrition_rate',
        'salary': 'avg_salary'
    })
    
    # Diversity metrics
    gender_dist = df['gender'].value_counts(normalize=True) * 100
    education_dist = df['education'].value_counts(normalize=True) * 100
    
    return {
        'overall': metrics,
        'by_department': dept_metrics.reset_index().to_dict('records'),
        'by_position': position_metrics.reset_index().to_dict('records'),
        'gender_distribution': gender_dist.to_dict(),
        'education_distribution': education_dist.to_dict()
    }
