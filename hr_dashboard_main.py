import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import logging
import webbrowser
from pathlib import Path
import json
import datetime
import time
import schedule
from hr_html_generator import calculate_metrics, load_branding_config, generate_css
from hr_visualizations import create_visualizations
from hr_analytics_real_data import load_data
from hr_staffing_tracker import process_monthly_staffing, create_staffing_visualizations, analyze_optimal_hiring_time, create_monthly_staffing_table

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

def generate_html_report(metrics, dept_metrics, branding_config, monthly_staffing_table=None, best_hiring_months=None, worst_hiring_months=None):
    """Generate an HTML report with the metrics and visualizations"""
    logger.info("Generating HTML dashboard...")
    
    css_styles = generate_css(branding_config)
    last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Start building HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{branding_config['dashboard_title']}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {css_styles}
        </style>
    </head>
    <body>
        <div class="header-container">
            {"<img class='logo' src='" + branding_config['logo_url'] + "' alt='Company Logo'>" if branding_config['logo_url'] else ""}
            <h1>{branding_config['dashboard_title']}</h1>
        </div>
        
        <p class="last-updated">Last updated: {last_updated}</p>
        
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
                <div class="metric-label">Satisfaction</div>
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
            <h2>Employee Satisfaction & Retention</h2>
            <div class="charts-row">
                <div class="chart-container">
                    <h3>Tenure vs Job Satisfaction</h3>
                    <img class="chart-img" src="images/tenure_vs_satisfaction.png" alt="Tenure vs Satisfaction">
                    <p><small>Blue dots represent active employees; red dots represent those who left the company.</small></p>
                </div>
                <div class="chart-container">
                    <h3>Attrition by Department</h3>
                    <img class="chart-img" src="images/attrition_by_dept.png" alt="Attrition by Department">
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Employee Tenure</h2>
            <div class="charts-row">
                <div class="chart-container" style="width: 100%;">
                    <h3>Years of Service Distribution</h3>
                    <img class="chart-img" src="images/tenure_distribution.png" alt="Tenure Distribution">
                </div>
            </div>
        </div>
    """
    
    # Add satisfaction correlation heatmap if available
    if os.path.exists(images_dir / "satisfaction_correlation.png"):
        html += """
        <div class="section">
            <h2>Satisfaction Metrics Correlation</h2>
            <div class="charts-row">
                <div class="chart-container" style="width: 100%;">
                    <h3>Correlation Between Satisfaction Metrics</h3>
                    <img class="chart-img" src="images/satisfaction_correlation.png" alt="Satisfaction Correlation">
                </div>
            </div>
        </div>
        """
    
    # Department-wise metrics table
    html += """
        <div class="section">
            <h2>Department-wise Metrics</h2>
            <table>
                <tr>
                    <th>Department</th>
                    <th>Employee Count</th>
                    <th>Attrition Rate</th>
                    <th>Avg. Salary</th>
    """
    
    # Add satisfaction column header if available
    if 'Avg. Satisfaction' in dept_metrics.columns:
        html += """
                    <th>Avg. Satisfaction</th>
        """
    
    html += """
                </tr>
    """
    
    # Add table rows
    for _, row in dept_metrics.iterrows():
        html += f"""
                <tr>
                    <td>{row['department']}</td>
                    <td>{row['Employee Count']}</td>
                    <td>{row['Attrition Rate']}</td>
                    <td>{row['Avg. Salary']}</td>
        """
        
        # Add satisfaction value if available
        if 'Avg. Satisfaction' in dept_metrics.columns:
            html += f"""
                    <td>{row['Avg. Satisfaction']}</td>
            """
        
        html += """
                </tr>
        """
    
    # Add manpower planning section if monthly data is available
    if monthly_staffing_table:
        html += """
        <div class="section manpower-planning">
            <h2>Manpower Planning & Staffing Trends</h2>
            <p class="section-description">This section helps HR teams track staffing levels over time and plan for future hiring needs based on attrition patterns.</p>
            
            <div class="charts-row">
                <div class="chart-container">
                    <h3>Monthly Headcount Trend</h3>
                    <img class="chart-img" src="images/monthly_headcount.png" alt="Monthly Headcount Trend">
                </div>
                <div class="chart-container">
                    <h3>Monthly Staff Movement</h3>
                    <img class="chart-img" src="images/monthly_movement.png" alt="Monthly Staff Movement">
                </div>
            </div>
            
            <div class="charts-row">
                <div class="chart-container">
                    <h3>Monthly Attrition Rate</h3>
                    <img class="chart-img" src="images/monthly_attrition_rate.png" alt="Monthly Attrition Rate">
                    <p><small>Red dotted line represents the 5% attrition threshold where action may be required.</small></p>
                </div>
        """
        
        # Add staffing forecast chart if available
        if os.path.exists(images_dir / "staffing_forecast.png"):
            html += """
                <div class="chart-container">
                    <h3>Staffing Forecast (Next 6 Months)</h3>
                    <img class="chart-img" src="images/staffing_forecast.png" alt="Staffing Forecast">
                </div>
            """
        
        html += """
            </div>
            
            <h3>Monthly Staffing Data</h3>
            <div class="table-responsive">
                %s
            </div>
        """ % monthly_staffing_table
        
        # Add seasonal hiring pattern if available
        if os.path.exists(images_dir / "seasonal_hiring_pattern.png"):
            html += """
            <div class="charts-row">
                <div class="chart-container" style="width: 100%;">
                    <h3>Seasonal Hiring and Attrition Patterns</h3>
                    <img class="chart-img" src="images/seasonal_hiring_pattern.png" alt="Seasonal Hiring Pattern">
                </div>
            </div>
            """
        
        # Add hiring recommendations if available
        if best_hiring_months and worst_hiring_months:
            html += """
            <div class="hiring-recommendations">
                <h3>Hiring Planning Recommendations</h3>
                <div class="recommendation-boxes">
                    <div class="recommendation-box good">
                        <h4>Best Months to Start Hiring</h4>
                        <p>%s</p>
                        <p><small>Based on historical patterns of low attrition and high joining rates</small></p>
                    </div>
                    <div class="recommendation-box bad">
                        <h4>Months to Avoid Hiring</h4>
                        <p>%s</p>
                        <p><small>These months historically have high attrition or low joining success</small></p>
                    </div>
                </div>
            </div>
            """ % (', '.join(best_hiring_months), ', '.join(worst_hiring_months))
        
        html += """
        </div>
        """

    # Close the page and add footer
    html += f"""
        <div class="footer">
            <p>&copy; {datetime.datetime.now().year} {branding_config['company_name']} - HR Analytics Dashboard</p>
            <p>Generated on {datetime.datetime.now().strftime("%Y-%m-%d at %H:%M")}</p>
        </div>
    </body>
    </html>
    """
    
    # Write HTML to file
    html_file = output_dir / "hr_dashboard.html"
    with open(html_file, "w") as f:
        f.write(html)
    
    return html_file

def generate_dashboard(data_file=None, config_file=None, open_browser=True):
    """Generate the complete HR Analytics Dashboard with manpower planning"""
    start_time = time.time()
    logger.info("Starting HR Analytics Dashboard generation...")
    
    # Load data
    df = load_data(data_file)
    
    # Save the data to CSV if it's generated sample data
    if data_file is None or not os.path.exists(data_file):
        df.to_csv(output_dir / "hr_data.csv", index=False)
        logger.info(f"Sample HR data saved to {output_dir / 'hr_data.csv'}")
    
    # Process monthly staffing data for manpower planning
    monthly_df = process_monthly_staffing(df)
    
    # Create standard visualizations
    create_visualizations(df, images_dir)
    
    # Create staffing trend visualizations
    create_staffing_visualizations(monthly_df, images_dir)
    
    # Analyze optimal hiring timing if enough data
    best_hiring_months = None
    worst_hiring_months = None
    if monthly_df is not None and len(monthly_df) >= 12:
        best_hiring_months, worst_hiring_months = analyze_optimal_hiring_time(monthly_df, images_dir)
    
    # Generate monthly staffing table HTML
    monthly_staffing_table = create_monthly_staffing_table(monthly_df)
    
    # Calculate metrics
    metrics, dept_metrics = calculate_metrics(df)
    
    # Add manpower planning metrics
    if monthly_df is not None and len(monthly_df) > 0:
        metrics['avg_monthly_attrition'] = f"{monthly_df['attrition_rate'].mean():.1f}%"
        metrics['current_month_headcount'] = monthly_df.iloc[-1]['headcount'] if not monthly_df.empty else 'N/A'
        metrics['last_month_leavers'] = monthly_df.iloc[-1]['leavers'] if not monthly_df.empty else 'N/A'
    
    # Load branding configuration
    branding_config = load_branding_config(config_file)
    
    # Generate HTML report with manpower planning section
    html_file = generate_html_report(
        metrics, 
        dept_metrics, 
        branding_config, 
        monthly_staffing_table=monthly_staffing_table, 
        best_hiring_months=best_hiring_months,
        worst_hiring_months=worst_hiring_months
    )
    
    end_time = time.time()
    logger.info(f"Dashboard generated successfully in {end_time - start_time:.2f} seconds!")
    logger.info(f"Dashboard file: {html_file.resolve()}")
    
    # Try to automatically open the HTML file in the default browser
    if open_browser:
        try:
            webbrowser.open(html_file.resolve().as_uri())
            logger.info("Opened dashboard in web browser.")
        except Exception as e:
            logger.error(f"Couldn't automatically open the browser: {e}")
            logger.info("Please open the HTML file manually.")
    
    return html_file

def schedule_generation(data_file=None, config_file=None, schedule_interval="daily", specific_time="09:00"):
    """
    Schedule regular dashboard generation
    
    Args:
        data_file: Path to HR data file
        config_file: Path to branding configuration
        schedule_interval: 'hourly', 'daily', or 'weekly'
        specific_time: Time for daily or weekly updates (format: HH:MM)
    """
    logger.info(f"Setting up {schedule_interval} dashboard generation at {specific_time}")
    
    # Define the job function
    def job():
        logger.info("Running scheduled dashboard generation...")
        generate_dashboard(data_file, config_file, open_browser=False)
        logger.info("Scheduled dashboard generation completed.")
    
    # Set up the schedule
    if schedule_interval == "hourly":
        schedule.every().hour.do(job)
    elif schedule_interval == "daily":
        schedule.every().day.at(specific_time).do(job)
    elif schedule_interval == "weekly":
        schedule.every().monday.at(specific_time).do(job)
    
    # Generate the dashboard once immediately
    job()
    
    # Keep the script running to maintain the schedule
    logger.info(f"Dashboard will be regenerated {schedule_interval} at {specific_time}")
    logger.info("Press Ctrl+C to stop the scheduler...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped.")

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='HR Analytics Dashboard Generator')
    parser.add_argument('--data', type=str, help='Path to HR data CSV/Excel file')
    parser.add_argument('--config', type=str, help='Path to branding configuration JSON file')
    parser.add_argument('--schedule', type=str, choices=['hourly', 'daily', 'weekly'], 
                        help='Schedule automatic dashboard generation')
    parser.add_argument('--time', type=str, default='09:00', 
                        help='Time for scheduled generation (format: HH:MM, default: 09:00)')
    parser.add_argument('--no-browser', action='store_true', 
                        help='Disable automatic browser opening')
    
    args = parser.parse_args()
    
    if args.schedule:
        schedule_generation(args.data, args.config, args.schedule, args.time)
    else:
        generate_dashboard(args.data, args.config, not args.no_browser)

if __name__ == "__main__":
    main()
