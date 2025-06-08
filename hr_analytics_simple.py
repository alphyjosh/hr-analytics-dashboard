import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Create output directory for HTML and images
output_dir = Path("hr_analytics_output")
output_dir.mkdir(exist_ok=True)
images_dir = output_dir / "images"
images_dir.mkdir(exist_ok=True)

# Generate sample HR data
def generate_sample_data(n_employees=100):
    """Generate sample HR data for demonstration"""
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
    
    return pd.DataFrame(data)

# Create visualizations
def create_visualizations(df):
    """Create basic visualizations and save them as PNG files"""
    # 1. Attrition Distribution Pie Chart
    plt.figure(figsize=(8, 6))
    labels = ['Active', 'Left']
    sizes = [len(df[df['attrition'] == 0]), len(df[df['attrition'] == 1])]
    explode = (0, 0.1)
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')
    plt.title('Employee Attrition Distribution')
    plt.savefig(images_dir / 'attrition_pie.png')
    plt.close()
    
    # 2. Department Distribution Bar Chart
    plt.figure(figsize=(10, 6))
    dept_counts = df['department'].value_counts()
    dept_counts.plot(kind='bar', color='skyblue')
    plt.title('Employee Distribution by Department')
    plt.xlabel('Department')
    plt.ylabel('Number of Employees')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(images_dir / 'department_distribution.png')
    plt.close()
    
    # 3. Salary Distribution Histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df['salary'], bins=20, color='green', alpha=0.7)
    plt.title('Salary Distribution')
    plt.xlabel('Annual Salary ($)')
    plt.ylabel('Number of Employees')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(images_dir / 'salary_histogram.png')
    plt.close()
    
    # 4. Age Distribution Histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df['age'], bins=15, color='purple', alpha=0.7)
    plt.title('Age Distribution')
    plt.xlabel('Age')
    plt.ylabel('Number of Employees')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(images_dir / 'age_histogram.png')
    plt.close()
    
    # 5. Tenure vs Satisfaction Scatter Plot
    plt.figure(figsize=(10, 6))
    colors = ['blue' if a == 0 else 'red' for a in df['attrition']]
    plt.scatter(df['tenure'], df['satisfaction'], c=colors, alpha=0.6)
    plt.title('Tenure vs Job Satisfaction')
    plt.xlabel('Tenure (Years)')
    plt.ylabel('Job Satisfaction (1-5)')
    plt.grid(True, alpha=0.3)
    plt.savefig(images_dir / 'tenure_vs_satisfaction.png')
    plt.close()

def calculate_metrics(df):
    """Calculate key HR metrics"""
    metrics = {
        'total_employees': len(df),
        'attrition_rate': f"{df['attrition'].mean() * 100:.1f}%",
        'avg_salary': f"${df['salary'].mean():,.0f}",
        'avg_satisfaction': f"{df['satisfaction'].mean():.1f}/5.0",
        'avg_tenure': f"{df['tenure'].mean():.1f} years"
    }
    
    # Department-wise metrics
    dept_metrics = df.groupby('department').agg({
        'employee_id': 'count',
        'attrition': lambda x: f"{x.mean() * 100:.1f}%",
        'salary': lambda x: f"${x.mean():,.0f}",
        'satisfaction': lambda x: f"{x.mean():.1f}"
    }).rename(columns={
        'employee_id': 'Employee Count',
        'attrition': 'Attrition Rate',
        'salary': 'Avg. Salary',
        'satisfaction': 'Avg. Satisfaction'
    })
    
    return metrics, dept_metrics.reset_index()

def generate_html_report(metrics, dept_metrics):
    """Generate an HTML report with the metrics and visualizations"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HR Analytics Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
            h1 {{ color: #1f77b4; text-align: center; margin-bottom: 30px; }}
            .metrics-row {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
            .metric-card {{ background-color: #f8f9fa; border-radius: 10px; padding: 15px; width: 18%; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #1f77b4; margin-bottom: 8px; }}
            .metric-label {{ font-size: 14px; color: #6c757d; }}
            .section {{ margin-bottom: 40px; }}
            .charts-row {{ display: flex; justify-content: space-between; flex-wrap: wrap; }}
            .chart-container {{ width: 48%; margin-bottom: 20px; background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .chart-img {{ width: 100%; height: auto; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #1f77b4; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .footer {{ text-align: center; margin-top: 40px; color: #6c757d; font-size: 14px; }}
        </style>
    </head>
    <body>
        <h1>HR Analytics Dashboard</h1>
        
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-value">{metrics['total_employees']}</div>
                <div class="metric-label">Total Employees</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['attrition_rate']}</div>
                <div class="metric-label">Attrition Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['avg_salary']}</div>
                <div class="metric-label">Avg. Salary</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['avg_satisfaction']}</div>
                <div class="metric-label">Avg. Satisfaction</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['avg_tenure']}</div>
                <div class="metric-label">Avg. Tenure</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Employee Distribution</h2>
            <div class="charts-row">
                <div class="chart-container">
                    <h3>Attrition Distribution</h3>
                    <img class="chart-img" src="images/attrition_pie.png" alt="Attrition Distribution">
                </div>
                <div class="chart-container">
                    <h3>Department Distribution</h3>
                    <img class="chart-img" src="images/department_distribution.png" alt="Department Distribution">
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Employee Demographics</h2>
            <div class="charts-row">
                <div class="chart-container">
                    <h3>Salary Distribution</h3>
                    <img class="chart-img" src="images/salary_histogram.png" alt="Salary Distribution">
                </div>
                <div class="chart-container">
                    <h3>Age Distribution</h3>
                    <img class="chart-img" src="images/age_histogram.png" alt="Age Distribution">
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Employee Satisfaction Analysis</h2>
            <div class="charts-row">
                <div class="chart-container" style="width: 100%;">
                    <h3>Tenure vs Job Satisfaction</h3>
                    <img class="chart-img" src="images/tenure_vs_satisfaction.png" alt="Tenure vs Satisfaction">
                    <p><small>Blue dots represent active employees; red dots represent those who left the company.</small></p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Department-wise Metrics</h2>
            <table>
                <tr>
                    <th>Department</th>
                    <th>Employee Count</th>
                    <th>Attrition Rate</th>
                    <th>Avg. Salary</th>
                    <th>Avg. Satisfaction</th>
                </tr>
    """
    
    for _, row in dept_metrics.iterrows():
        html += f"""
                <tr>
                    <td>{row['department']}</td>
                    <td>{row['Employee Count']}</td>
                    <td>{row['Attrition Rate']}</td>
                    <td>{row['Avg. Salary']}</td>
                    <td>{row['Avg. Satisfaction']}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <div class="footer">
            <p>HR Analytics Dashboard - Generated on {}</p>
        </div>
    </body>
    </html>
    """.format(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"))
    
    with open(output_dir / "hr_analytics_dashboard.html", "w") as f:
        f.write(html)
    
    return output_dir / "hr_analytics_dashboard.html"

def main():
    print("Generating HR Analytics Dashboard...")
    
    # Generate sample data
    df = generate_sample_data()
    
    # Save the data to CSV
    df.to_csv(output_dir / "hr_data.csv", index=False)
    print(f"Sample HR data saved to {output_dir / 'hr_data.csv'}")
    
    # Create visualizations
    print("Creating visualizations...")
    create_visualizations(df)
    
    # Calculate metrics
    print("Calculating metrics...")
    metrics, dept_metrics = calculate_metrics(df)
    
    # Generate HTML report
    print("Generating HTML dashboard...")
    html_file = generate_html_report(metrics, dept_metrics)
    
    print(f"\nDashboard generated successfully! Open this file in your browser:")
    print(f"{html_file.resolve()}")
    
    # Try to automatically open the HTML file in the default browser
    try:
        import webbrowser
        webbrowser.open(html_file.resolve().as_uri())
        print("\nOpened dashboard in web browser.")
    except Exception as e:
        print(f"\nCouldn't automatically open the browser: {e}")
        print("Please open the HTML file manually.")

if __name__ == "__main__":
    main()
