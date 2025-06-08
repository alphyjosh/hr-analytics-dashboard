import pandas as pd
import logging
from pathlib import Path
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def calculate_metrics(df):
    """Calculate key HR metrics from the dataset"""
    logger.info("Calculating HR metrics...")
    
    metrics = {}
    
    # Overall metrics
    metrics['total_employees'] = len(df)
    metrics['attrition_rate'] = f"{df['attrition'].mean() * 100:.1f}%"
    metrics['avg_salary'] = f"${df['salary'].mean():,.0f}"
    metrics['avg_satisfaction'] = f"{df['satisfaction'].mean():.1f}/5.0" if 'satisfaction' in df.columns else 'N/A'
    metrics['avg_tenure'] = f"{df['tenure'].mean():.1f} years"
    
    # Department-wise metrics
    dept_metrics = df.groupby('department').agg({
        'employee_id': 'count',
        'attrition': lambda x: f"{x.mean() * 100:.1f}%",
        'salary': lambda x: f"${x.mean():,.0f}",
    })
    
    if 'satisfaction' in df.columns:
        dept_metrics['satisfaction'] = df.groupby('department')['satisfaction'].agg(lambda x: f"{x.mean():.1f}")
    
    dept_metrics = dept_metrics.rename(columns={
        'employee_id': 'Employee Count',
        'attrition': 'Attrition Rate',
        'salary': 'Avg. Salary',
        'satisfaction': 'Avg. Satisfaction'
    }).reset_index()
    
    return metrics, dept_metrics

def load_branding_config(config_file=None):
    """Load branding configuration from a JSON file or return defaults"""
    default_config = {
        "company_name": "Your Company",
        "logo_url": "",
        "primary_color": "#1f77b4",
        "secondary_color": "#ff7f0e",
        "accent_color": "#2ca02c",
        "font_family": "Arial, sans-serif",
        "dashboard_title": "HR Analytics Dashboard"
    }
    
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Update default config with loaded values
                for key, value in config.items():
                    if key in default_config and value:
                        default_config[key] = value
            logger.info(f"Loaded branding configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    return default_config

def generate_css(branding):
    """Generate CSS based on branding configuration"""
    return f"""
    body {{ 
        font-family: {branding['font_family']}; 
        margin: 0; 
        padding: 20px; 
        color: #333; 
        background-color: #f9f9f9;
    }}
    h1 {{ 
        color: {branding['primary_color']}; 
        text-align: center; 
        margin-bottom: 30px; 
        padding: 10px;
        border-bottom: 3px solid {branding['secondary_color']};
    }}
    h3 {{
        color: {branding['primary_color']};
        margin-top: 20px;
        margin-bottom: 15px;
    }}
    h4 {{
        color: {branding['secondary_color']};
        margin-top: 15px;
        margin-bottom: 10px;
    }}
    .metrics-row {{ 
        display: flex; 
        justify-content: space-between; 
        flex-wrap: wrap;
        margin-bottom: 30px; 
    }}
    .metric-card {{ 
        background-color: white; 
        border-radius: 10px; 
        padding: 20px 15px; 
        width: 18%; 
        text-align: center; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        transition: transform 0.3s ease;
        border-top: 4px solid {branding['primary_color']};
        min-width: 150px;
        margin-bottom: 15px;
    }}
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }}
    .metric-value {{ 
        font-size: 28px; 
        font-weight: bold; 
        color: {branding['primary_color']}; 
        margin-bottom: 10px; 
    }}
    .metric-label {{ 
        font-size: 14px; 
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }}
    .section {{ 
        margin-bottom: 40px; 
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .section-description {{
        color: #6c757d;
        font-style: italic;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px dashed #e0e0e0;
    }}
    .charts-row {{ 
        display: flex; 
        justify-content: space-between; 
        flex-wrap: wrap; 
    }}
    .chart-container {{ 
        width: 48%; 
        margin-bottom: 20px; 
        background-color: white; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
    }}
    .chart-img {{ 
        width: 100%; 
        height: auto; 
    }}
    h2 {{ 
        color: {branding['secondary_color']}; 
        border-bottom: 2px solid #eee; 
        padding-bottom: 10px; 
    }}
    /* Regular table styles */
    table {{ 
        width: 100%; 
        border-collapse: collapse; 
        margin: 25px 0; 
        font-size: 14px;
    }}
    th, td {{ 
        padding: 12px 15px; 
        text-align: left; 
        border-bottom: 1px solid #ddd; 
    }}
    th {{ 
        background-color: {branding['primary_color']}; 
        color: white; 
        position: sticky;
        top: 0;
    }}
    tr:hover {{ 
        background-color: #f5f5f5; 
    }}
    /* Staffing table specific styles */
    .staffing-table {{
        margin-top: 15px;
        font-size: 14px;
        width: 100%;
    }}
    .staffing-table th {{
        background-color: {branding['secondary_color']};
        color: white;
        text-align: center;
        padding: 10px;
    }}
    .staffing-table td {{
        text-align: center;
        padding: 8px;
    }}
    .staffing-table tr:nth-child(even) {{
        background-color: #f7f7f7;
    }}
    .table-responsive {{
        overflow-x: auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 5px;
        margin: 20px 0;
    }}
    .high-attrition {{
        color: white;
        background-color: #dc3545;
        font-weight: bold;
    }}
    /* Recommendation boxes */
    .hiring-recommendations {{
        margin-top: 30px;
    }}
    .recommendation-boxes {{
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 15px;
    }}
    .recommendation-box {{
        padding: 20px;
        border-radius: 10px;
        width: calc(50% - 20px);
        box-sizing: border-box;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .recommendation-box p {{
        font-size: 18px;
        font-weight: 600;
    }}
    .recommendation-box small {{
        color: #6c757d;
        font-style: italic;
    }}
    .recommendation-box.good {{
        background-color: #e8f5e9;
        border-left: 5px solid #28a745;
    }}
    .recommendation-box.bad {{
        background-color: #ffebee;
        border-left: 5px solid #dc3545;
    }}
    /* General styles */
    .footer {{ 
        text-align: center; 
        margin-top: 40px; 
        color: #6c757d; 
        font-size: 14px; 
        padding: 20px;
        border-top: 1px solid #eee;
    }}
    .logo {{ 
        max-height: 60px; 
        margin-bottom: 20px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }}
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }}
    .last-updated {{
        font-style: italic;
        color: #6c757d;
        text-align: right;
        margin-top: -20px;
        margin-bottom: 20px;
    }}
    /* Responsive styles */
    @media (max-width: 768px) {{
        .metric-card {{ width: 45%; }}
        .chart-container {{ width: 100%; }}
        .recommendation-box {{ width: 100%; }}
    }}
    """
