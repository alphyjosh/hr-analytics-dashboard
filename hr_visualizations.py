import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_visualizations(df, images_dir):
    """
    Create enhanced visualizations and save them as PNG files
    
    Args:
        df (pd.DataFrame): DataFrame containing HR data
        images_dir (Path): Directory to save generated images
    """
    logger.info("Creating visualizations...")
    
    # Set the style for all visualizations
    plt.style.use('ggplot')
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # 1. Attrition Distribution Pie Chart
    logger.info("Creating attrition pie chart...")
    plt.figure(figsize=(8, 6))
    labels = ['Active', 'Left']
    sizes = [len(df[df['attrition'] == 0]), len(df[df['attrition'] == 1])]
    explode = (0, 0.1)
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', 
            shadow=True, startangle=90, colors=[colors[0], colors[3]])
    plt.axis('equal')
    plt.title('Employee Attrition Distribution', fontsize=16)
    plt.savefig(images_dir / 'attrition_pie.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Department Distribution Bar Chart
    logger.info("Creating department distribution chart...")
    plt.figure(figsize=(10, 6))
    dept_counts = df['department'].value_counts()
    ax = dept_counts.plot(kind='bar', color=colors[0])
    ax.set_title('Employee Distribution by Department', fontsize=16)
    ax.set_xlabel('Department', fontsize=12)
    ax.set_ylabel('Number of Employees', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels on top of bars
    for i, v in enumerate(dept_counts):
        ax.text(i, v + 0.5, str(v), ha='center', fontsize=10)
        
    plt.tight_layout()
    plt.savefig(images_dir / 'department_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Salary Distribution Histogram
    logger.info("Creating salary distribution histogram...")
    plt.figure(figsize=(10, 6))
    sns.histplot(df['salary'], bins=20, kde=True, color=colors[1])
    plt.title('Salary Distribution', fontsize=16)
    plt.xlabel('Annual Salary ($)', fontsize=12)
    plt.ylabel('Number of Employees', fontsize=12)
    plt.grid(axis='y', alpha=0.75)
    
    # Add median and mean lines
    median_salary = df['salary'].median()
    mean_salary = df['salary'].mean()
    plt.axvline(median_salary, color=colors[2], linestyle='--', linewidth=2, label=f'Median: ${median_salary:,.0f}')
    plt.axvline(mean_salary, color=colors[3], linestyle='--', linewidth=2, label=f'Mean: ${mean_salary:,.0f}')
    plt.legend()
    
    plt.savefig(images_dir / 'salary_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Age Distribution Histogram
    logger.info("Creating age distribution histogram...")
    plt.figure(figsize=(10, 6))
    sns.histplot(df['age'], bins=15, kde=True, color=colors[4])
    plt.title('Age Distribution', fontsize=16)
    plt.xlabel('Age', fontsize=12)
    plt.ylabel('Number of Employees', fontsize=12)
    plt.grid(axis='y', alpha=0.75)
    
    # Add age groups annotation
    age_groups = df['age'].value_counts(bins=[20, 30, 40, 50, 60, 70]).sort_index()
    age_labels = ['20-30', '30-40', '40-50', '50-60', '60+']
    age_data = [age_groups.get(i, 0) for i in range(len(age_labels))]
    
    # Add text annotation
    plt.annotate(
        f"Age Groups:\n" + "\n".join([f"{label}: {count}" for label, count in zip(age_labels, age_data) if count > 0]),
        xy=(0.02, 0.70),
        xycoords='axes fraction',
        bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8)
    )
    
    plt.savefig(images_dir / 'age_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Tenure vs Satisfaction Scatter Plot with regression line
    logger.info("Creating tenure vs satisfaction scatter plot...")
    plt.figure(figsize=(10, 6))
    
    # Create a scatter plot
    sns.scatterplot(
        x='tenure', 
        y='satisfaction',
        hue='attrition',
        palette={0: colors[0], 1: colors[3]},
        s=100,
        alpha=0.7,
        data=df
    )
    
    # Add regression line
    sns.regplot(
        x='tenure', 
        y='satisfaction',
        scatter=False,
        ci=None,
        line_kws={"color": "black", "lw": 2, "linestyle": "--"},
        data=df
    )
    
    plt.title('Tenure vs Job Satisfaction', fontsize=16)
    plt.xlabel('Tenure (Years)', fontsize=12)
    plt.ylabel('Job Satisfaction (1-5)', fontsize=12)
    plt.legend(title='Attrition', labels=['Active', 'Left'])
    plt.grid(True, alpha=0.3)
    plt.savefig(images_dir / 'tenure_vs_satisfaction.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. NEW: Attrition by Department
    logger.info("Creating attrition by department chart...")
    plt.figure(figsize=(12, 6))
    
    attrition_by_dept = df.groupby('department')['attrition'].mean() * 100
    ax = attrition_by_dept.plot(kind='bar', color=colors[3])
    ax.set_title('Attrition Rate by Department (%)', fontsize=16)
    ax.set_xlabel('Department', fontsize=12)
    ax.set_ylabel('Attrition Rate (%)', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels on top of bars
    for i, v in enumerate(attrition_by_dept):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(images_dir / 'attrition_by_dept.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 7. NEW: Satisfaction Heatmap
    logger.info("Creating satisfaction heatmap...")
    if all(x in df.columns for x in ['satisfaction', 'work_life_balance', 'performance_rating']):
        plt.figure(figsize=(10, 8))
        
        # Create correlation matrix
        satisfaction_cols = ['satisfaction', 'work_life_balance', 'performance_rating']
        corr_matrix = df[satisfaction_cols].corr()
        
        # Generate heatmap
        sns.heatmap(
            corr_matrix, 
            annot=True, 
            cmap='coolwarm', 
            linewidths=0.5, 
            vmin=-1, 
            vmax=1
        )
        
        plt.title('Correlation Between Satisfaction Metrics', fontsize=16)
        plt.tight_layout()
        plt.savefig(images_dir / 'satisfaction_correlation.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 8. NEW: Years of Service Distribution
    logger.info("Creating years of service distribution...")
    plt.figure(figsize=(10, 6))
    
    bins = [0, 1, 3, 5, 10, 15, 20, 30]
    labels = ['<1 year', '1-3 years', '3-5 years', '5-10 years', '10-15 years', '15-20 years', '20+ years']
    
    df['tenure_group'] = pd.cut(df['tenure'], bins=bins, labels=labels, right=False)
    tenure_dist = df['tenure_group'].value_counts().sort_index()
    
    ax = tenure_dist.plot(kind='bar', color=colors[2])
    ax.set_title('Employee Tenure Distribution', fontsize=16)
    ax.set_xlabel('Years of Service', fontsize=12)
    ax.set_ylabel('Number of Employees', fontsize=12)
    
    # Add value labels on top of bars
    for i, v in enumerate(tenure_dist):
        ax.text(i, v + 0.5, str(v), ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(images_dir / 'tenure_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info("All visualizations created successfully.")
    return True
