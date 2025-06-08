from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import logging
import json
import datetime
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
from hr_staffing_tracker import create_staffing_visualizations
from hr_html_generator import calculate_metrics, load_branding_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create app
app = Flask(__name__)
# Use environment variable for secret key in production, or generate a random one
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())  # Required for session management

# Create output directory for static files
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
images_dir = static_dir / "images"
images_dir.mkdir(exist_ok=True)

# Default monthly data for demonstration
DEFAULT_MONTHS = ['Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025', 'May 2025', 'Jun 2025']
DEFAULT_HEADCOUNT = [120, 125, 128, 130, 132, 135]
DEFAULT_JOINERS = [8, 7, 5, 6, 4, 6]  
DEFAULT_LEAVERS = [3, 2, 2, 4, 2, 3]

def format_plot_to_base64(fig):
    """Convert matplotlib figure to base64 encoded image for HTML embedding"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_str

def calculate_attrition_rates(headcount, leavers):
    """Calculate attrition rates as percentages"""
    return [(leavers[i] / headcount[i] * 100) if headcount[i] > 0 else 0 for i in range(len(headcount))]

def create_headcount_chart(months, headcount):
    """Create headcount trend chart"""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(months, headcount, marker='o', linewidth=2, color='#1f77b4')
    ax.set_title('Monthly Headcount Trend', fontsize=14)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Total Staff', fontsize=12)
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return format_plot_to_base64(fig)

def create_movement_chart(months, joiners, leavers):
    """Create staff movement chart (joiners vs leavers)"""
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.35
    x = np.arange(len(months))
    
    ax.bar(x - width/2, joiners, width, label='New Joiners', color='#2ca02c')
    ax.bar(x + width/2, leavers, width, label='Leavers', color='#d62728')
    
    ax.set_title('Monthly Staff Movement', fontsize=14)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Number of Employees', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45)
    ax.legend()
    ax.grid(True, axis='y')
    plt.tight_layout()
    return format_plot_to_base64(fig)

def create_attrition_chart(months, attrition_rates):
    """Create attrition rate chart"""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(months, attrition_rates, marker='o', linewidth=2, color='#d62728')
    ax.set_title('Monthly Attrition Rate (%)', fontsize=14)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Attrition Rate (%)', fontsize=12)
    ax.grid(True)
    plt.xticks(rotation=45)
    
    # Add threshold line at 5%
    ax.axhline(y=5, color='red', linestyle='--', alpha=0.7, label='5% Threshold')
    ax.legend()
    
    # Annotate high attrition points
    for i, rate in enumerate(attrition_rates):
        if rate > 5:  # Highlighting high attrition months
            ax.annotate(f'{rate:.1f}%', 
                       (i, rate),
                       textcoords="offset points",
                       xytext=(0,10),
                       ha='center')
    
    plt.tight_layout()
    return format_plot_to_base64(fig)

def create_forecast_chart(months, headcount):
    """Create forecast chart based on trend"""
    # Only create forecast if we have enough historical data
    if len(months) < 3:
        return None
    
    # Calculate average monthly change
    avg_change = np.mean(np.diff(headcount))
    
    # Project for next 3 months
    last_month = headcount[-1]
    forecast_months = [f'Forecast {i+1}' for i in range(3)]
    forecast_values = [last_month + (i+1)*avg_change for i in range(3)]
    
    # Create forecast visualization
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot historical data
    ax.plot(months, headcount, marker='o', linewidth=2, color='#1f77b4', label='Historical')
    
    # Plot forecast
    ax.plot(range(len(months), len(months)+len(forecast_months)), forecast_values, 
            marker='s', linewidth=2, linestyle='--', color='#9467bd', label='Forecast')
    
    # Add shaded area for forecast uncertainty
    upper_bound = [val * 1.1 for val in forecast_values]
    lower_bound = [val * 0.9 for val in forecast_values]
    ax.fill_between(range(len(months), len(months)+len(forecast_months)), 
                     upper_bound, lower_bound, color='#9467bd', alpha=0.2)
    
    # Configure axes
    full_x_range = months + forecast_months
    ax.set_xticks(range(len(full_x_range)))
    ax.set_xticklabels(full_x_range, rotation=45)
    ax.set_title('Staffing Forecast (Next 3 Months)', fontsize=14)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Projected Headcount', fontsize=12)
    ax.grid(True)
    ax.legend()
    
    # Calculate needed hiring
    avg_attrition_rate = np.mean(calculate_attrition_rates(headcount, [headcount[i] - headcount[i+1] + 
                                                                     (0 if i+1 >= len(headcount) else 0) 
                                                                     for i in range(len(headcount)-1)]))
    projected_hiring = int(last_month * avg_attrition_rate/100 * 3)
    
    # Add annotation about hiring needs
    ax.annotate(f"Projected Hiring Need: {projected_hiring} (3 months)",
               xy=(0.02, 0.02),
               xycoords='axes fraction',
               bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8))
    
    plt.tight_layout()
    return format_plot_to_base64(fig)

@app.route('/')
def index():
    """Main dashboard page"""
    # Get data from session or use defaults
    months = session.get('months', DEFAULT_MONTHS)
    headcount = session.get('headcount', DEFAULT_HEADCOUNT)
    joiners = session.get('joiners', DEFAULT_JOINERS)
    leavers = session.get('leavers', DEFAULT_LEAVERS)
    
    # Calculate attrition rates
    attrition_rates = calculate_attrition_rates(headcount, leavers)
    
    # Generate charts
    headcount_chart = create_headcount_chart(months, headcount)
    movement_chart = create_movement_chart(months, joiners, leavers)
    attrition_chart = create_attrition_chart(months, attrition_rates)
    forecast_chart = create_forecast_chart(months, headcount)
    
    # Calculate key metrics
    avg_headcount = sum(headcount) / len(headcount) if headcount else 0
    avg_attrition = sum(attrition_rates) / len(attrition_rates) if attrition_rates else 0
    total_joiners = sum(joiners)
    total_leavers = sum(leavers)
    net_growth = total_joiners - total_leavers
    
    return render_template('dashboard.html',
                          months=months,
                          headcount=headcount,
                          joiners=joiners,
                          leavers=leavers,
                          attrition_rates=attrition_rates,
                          headcount_chart=headcount_chart,
                          movement_chart=movement_chart,
                          attrition_chart=attrition_chart,
                          forecast_chart=forecast_chart,
                          avg_headcount=avg_headcount,
                          avg_attrition=avg_attrition,
                          total_joiners=total_joiners,
                          total_leavers=total_leavers,
                          net_growth=net_growth,
                          current_year=datetime.datetime.now().year)

@app.route('/edit-data', methods=['GET', 'POST'])
def edit_data():
    """Edit staffing data"""
    if request.method == 'POST':
        # Get form data
        months = request.form.getlist('month[]')
        headcount = [int(count) for count in request.form.getlist('headcount[]')]
        joiners = [int(count) for count in request.form.getlist('joiners[]')]
        leavers = [int(count) for count in request.form.getlist('leavers[]')]
        
        # Store in session
        session['months'] = months
        session['headcount'] = headcount
        session['joiners'] = joiners
        session['leavers'] = leavers
        
        flash('Data updated successfully!', 'success')
        return redirect(url_for('index'))
    
    # For GET request, use data from session or defaults
    months = session.get('months', DEFAULT_MONTHS)
    headcount = session.get('headcount', DEFAULT_HEADCOUNT)
    joiners = session.get('joiners', DEFAULT_JOINERS)
    leavers = session.get('leavers', DEFAULT_LEAVERS)
    
    return render_template('edit_data.html',
                          months=months,
                          headcount=headcount,
                          joiners=joiners,
                          leavers=leavers,
                          data_length=len(months))

@app.route('/add-month', methods=['POST'])
def add_month():
    """Add a new month of data"""
    # Get current data from session
    months = session.get('months', DEFAULT_MONTHS).copy()
    headcount = session.get('headcount', DEFAULT_HEADCOUNT).copy()
    joiners = session.get('joiners', DEFAULT_JOINERS).copy()
    leavers = session.get('leavers', DEFAULT_LEAVERS).copy()
    
    # Get new month details from form
    new_month = request.form.get('new_month')
    new_headcount = int(request.form.get('new_headcount'))
    new_joiners = int(request.form.get('new_joiners'))
    new_leavers = int(request.form.get('new_leavers'))
    
    # Add new data
    months.append(new_month)
    headcount.append(new_headcount)
    joiners.append(new_joiners)
    leavers.append(new_leavers)
    
    # Update session
    session['months'] = months
    session['headcount'] = headcount
    session['joiners'] = joiners
    session['leavers'] = leavers
    
    flash('New month added successfully!', 'success')
    return redirect(url_for('edit_data'))

@app.route('/remove-month/<int:index>', methods=['POST'])
def remove_month(index):
    """Remove a month of data"""
    # Get current data from session
    months = session.get('months', DEFAULT_MONTHS).copy()
    headcount = session.get('headcount', DEFAULT_HEADCOUNT).copy()
    joiners = session.get('joiners', DEFAULT_JOINERS).copy()
    leavers = session.get('leavers', DEFAULT_LEAVERS).copy()
    
    # Check if index is valid
    if 0 <= index < len(months):
        # Remove data at index
        months.pop(index)
        headcount.pop(index)
        joiners.pop(index)
        leavers.pop(index)
        
        # Update session
        session['months'] = months
        session['headcount'] = headcount
        session['joiners'] = joiners
        session['leavers'] = leavers
        
        flash('Month removed successfully!', 'success')
    else:
        flash('Invalid month index!', 'error')
    
    return redirect(url_for('edit_data'))

@app.route('/export-data', methods=['GET'])
def export_data():
    """Export staffing data to CSV"""
    # Get data from session
    months = session.get('months', DEFAULT_MONTHS)
    headcount = session.get('headcount', DEFAULT_HEADCOUNT)
    joiners = session.get('joiners', DEFAULT_JOINERS)
    leavers = session.get('leavers', DEFAULT_LEAVERS)
    attrition_rates = calculate_attrition_rates(headcount, leavers)
    
    # Create DataFrame
    data = {
        'Month': months,
        'Headcount': headcount,
        'Joiners': joiners,
        'Leavers': leavers,
        'Attrition_Rate': [f"{rate:.2f}%" for rate in attrition_rates]
    }
    df = pd.DataFrame(data)
    
    # Save to CSV string
    csv_data = df.to_csv(index=False)
    
    # Return as download
    return jsonify({
        'data': csv_data,
        'filename': f'hr_staffing_data_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
    })

@app.route('/branding', methods=['GET', 'POST'])
def branding():
    """Customize dashboard branding"""
    if request.method == 'POST':
        # Get form data
        branding_config = {
            'company_name': request.form.get('company_name', 'Your Company'),
            'primary_color': request.form.get('primary_color', '#1f77b4'),
            'secondary_color': request.form.get('secondary_color', '#ff7f0e'),
            'dashboard_title': request.form.get('dashboard_title', 'HR Analytics Dashboard')
        }
        
        # Store in session
        session['branding'] = branding_config
        
        flash('Branding updated successfully!', 'success')
        return redirect(url_for('index'))
    
    # For GET request, use data from session or defaults
    branding = session.get('branding', {
        'company_name': 'Your Company',
        'primary_color': '#1f77b4',
        'secondary_color': '#ff7f0e',
        'dashboard_title': 'HR Analytics Dashboard'
    })
    
    return render_template('branding.html', branding=branding)

@app.route('/reset-data', methods=['POST'])
def reset_data():
    """Reset all data to defaults"""
    # Clear session data
    if 'months' in session:
        session.pop('months')
    if 'headcount' in session:
        session.pop('headcount')
    if 'joiners' in session:
        session.pop('joiners')
    if 'leavers' in session:
        session.pop('leavers')
    
    flash('Data reset to defaults!', 'success')
    return redirect(url_for('index'))

@app.route('/help')
def help_page():
    """Help page with instructions"""
    return render_template('help.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error_code=500, message="Internal server error"), 500

# Ensure the app can run in both development and production environments
if __name__ == '__main__':
    # Create required directories
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Message for developers
    logger.info("HR Analytics Dashboard Web App starting...")
    logger.info("Access the dashboard at: http://localhost:5000")
    logger.info("To make this publicly accessible, deploy to a cloud platform like Render, Railway, or PythonAnywhere")
    
    # Run the app in development mode
    app.run(debug=True)
else:
    # In production, we'll be using Gunicorn or another WSGI server
    # Make sure all required directories exist
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Log that the app is starting in production mode
    logger.info("HR Analytics Dashboard starting in production mode")
    
    # In production, don't run with debug=True
    app.config['DEBUG'] = False
