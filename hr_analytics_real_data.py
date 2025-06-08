import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create output directory for HTML and images
output_dir = Path("hr_analytics_output")
output_dir.mkdir(exist_ok=True)
images_dir = output_dir / "images"
images_dir.mkdir(exist_ok=True)

def load_data(file_path=None):
    """
    Load HR data from a CSV or Excel file, or generate sample data if no file provided
    
    Args:
        file_path (str): Path to the CSV or Excel file containing HR data
        
    Returns:
        pd.DataFrame: DataFrame containing HR data
    """
    if file_path and os.path.exists(file_path):
        logger.info(f"Loading data from {file_path}")
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            logger.error("Unsupported file format. Please provide a CSV or Excel file.")
            raise ValueError("Unsupported file format")
        
        # Check if the DataFrame has the required columns
        required_columns = ['department', 'position', 'age', 'tenure', 'salary', 'gender', 'attrition']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"The following required columns are missing: {missing_columns}")
            logger.warning("Using sample data instead")
            return generate_sample_data()
        
        return df
    else:
        logger.info("No valid file path provided. Using generated sample data.")
        return generate_sample_data()

def generate_sample_data(n_employees=100):
    """Generate sample HR data for demonstration"""
    logger.info(f"Generating sample data with {n_employees} employee records")
    np.random.seed(42)
    
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance']
    positions = ['Manager', 'Senior', 'Mid-level', 'Junior', 'Intern']
    education = ["Bachelor's", "Master's", 'PhD', 'High School']
    
    data = {
        'employee_id': range(1, n_employees + 1),
        'department': np.random.choice(departments, n_employees),
        'position': np.random.choice(positions, n_employees),
        'age': np.random.normal(35, 8, n_employees).astype(int).clip(22, 65),
        'tenure': np.random.gamma(3, 1, n_employees).astype(int).clip(0, 15),
        'salary': np.random.normal(75000, 25000, n_employees).astype(int).clip(30000, 200000),
        'education': np.random.choice(education, n_employees),
        'gender': np.random.choice(['Male', 'Female', 'Other'], n_employees),
        'attrition': np.random.choice([0, 1], n_employees, p=[0.85, 0.15]),
        'satisfaction': np.random.randint(1, 6, n_employees),
        'performance_rating': np.random.randint(1, 6, n_employees)
    }
    
    # Add hire date
    end_date = pd.Timestamp('2025-06-08')  # Today's date for reference
    hire_dates = []
    for t in data['tenure']:
        days = int(365.25 * t)
        hire_date = end_date - pd.Timedelta(days=days)
        hire_dates.append(hire_date)
    
    data['hire_date'] = hire_dates
    
    return pd.DataFrame(data)

# Create visualizations - this will be on part 2
