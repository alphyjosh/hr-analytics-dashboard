import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from pathlib import Path
import seaborn as sns
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_monthly_staffing(df):
    """Process HR data to extract monthly staffing metrics
    
    Args:
        df (pd.DataFrame): DataFrame with HR data including hire_date and exit_date
        
    Returns:
        tuple: (monthly_headcount, monthly_attrition, monthly_joiners)
    """
    logger.info("Processing monthly staffing data")
    
    # Ensure dates are in datetime format
    if 'hire_date' not in df.columns:
        logger.warning("No hire_date column found, cannot process monthly staffing")
        return None, None, None
    
    # Convert date columns to datetime if they're not already
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    
    # Add exit_date for employees who left (attrition=1)
    if 'exit_date' not in df.columns:
        # Calculate approximate exit date for those who left (assume they left in the last year)
        today = pd.Timestamp('2025-06-08')  # Using current date as reference
        df['exit_date'] = np.where(
            df['attrition'] == 1,
            # Random date in the last 12 months for those who left
            [today - timedelta(days=np.random.randint(1, 365)) for _ in range(len(df))],
            pd.NaT  # NaT for current employees
        )
    else:
        df['exit_date'] = pd.to_datetime(df['exit_date'])
    
    # Find the earliest and latest dates in the dataset
    min_date = df['hire_date'].min().replace(day=1)
    if df['exit_date'].notna().any():
        max_date = max(df['exit_date'].max(), pd.Timestamp('2025-06-08'))
    else:
        max_date = pd.Timestamp('2025-06-08')
    
    # Create a date range by month
    months_range = pd.date_range(start=min_date, end=max_date, freq='MS')
    
    # Initialize tracking DataFrames
    monthly_data = []
    
    # For each month, calculate headcount, joiners and leavers
    for month_start in months_range:
        month_end = month_start + pd.offsets.MonthEnd(1)
        
        # Count active employees at month end
        active_count = sum(
            (df['hire_date'] <= month_end) & 
            ((df['exit_date'].isna()) | (df['exit_date'] > month_end))
        )
        
        # Count joiners in month
        joiners = sum(
            (df['hire_date'] >= month_start) & 
            (df['hire_date'] <= month_end)
        )
        
        # Count leavers in month
        leavers = sum(
            (df['exit_date'] >= month_start) & 
            (df['exit_date'] <= month_end)
        )
        
        # Calculate attrition rate (as percentage)
        attrition_rate = (leavers / active_count * 100) if active_count > 0 else 0
        
        monthly_data.append({
            'month': month_start.strftime('%Y-%m'),
            'headcount': active_count,
            'joiners': joiners,
            'leavers': leavers,
            'attrition_rate': round(attrition_rate, 2)
        })
    
    monthly_df = pd.DataFrame(monthly_data)
    return monthly_df

def create_staffing_visualizations(monthly_df, images_dir):
    """Create visualizations for staffing metrics
    
    Args:
        monthly_df (pd.DataFrame): DataFrame with monthly staffing data
        images_dir (Path): Directory to save images
    """
    if monthly_df is None or len(monthly_df) == 0:
        logger.warning("No monthly data available for visualization")
        return
    
    logger.info("Creating staffing trend visualizations")
    
    # Set style
    plt.style.use('ggplot')
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # 1. Monthly Headcount Trend
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_df['month'], monthly_df['headcount'], marker='o', linewidth=2, color=colors[0])
    plt.title('Monthly Headcount Trend', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Total Staff', fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(images_dir / 'monthly_headcount.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Monthly Joiners and Leavers
    plt.figure(figsize=(12, 6))
    width = 0.35
    x = np.arange(len(monthly_df))
    
    plt.bar(x - width/2, monthly_df['joiners'], width, label='New Joiners', color=colors[2])
    plt.bar(x + width/2, monthly_df['leavers'], width, label='Leavers', color=colors[3])
    
    plt.title('Monthly Staff Movement', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Number of Employees', fontsize=12)
    plt.xticks(x, monthly_df['month'], rotation=45)
    plt.legend()
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig(images_dir / 'monthly_movement.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Monthly Attrition Rate
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_df['month'], monthly_df['attrition_rate'], marker='o', linewidth=2, color=colors[3])
    plt.title('Monthly Attrition Rate (%)', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)
    
    # Add threshold line at 5%
    plt.axhline(y=5, color='red', linestyle='--', alpha=0.7, label='5% Threshold')
    plt.legend()
    
    # Annotate high attrition points
    for i, rate in enumerate(monthly_df['attrition_rate']):
        if rate > 5:  # Highlighting high attrition months
            plt.annotate(f'{rate}%', 
                        (monthly_df['month'][i], rate),
                        textcoords="offset points",
                        xytext=(0,10),
                        ha='center')
    
    plt.tight_layout()
    plt.savefig(images_dir / 'monthly_attrition_rate.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Forecast staffing needs (simple trend-based forecast)
    if len(monthly_df) >= 6:  # Only forecast if we have enough historical data
        # Take the last 6 months of data for forecasting
        recent_data = monthly_df.tail(6)
        
        # Calculate average monthly change in headcount
        avg_monthly_change = np.mean(np.diff(recent_data['headcount']))
        
        # Calculate average monthly attrition
        avg_attrition_rate = np.mean(recent_data['attrition_rate'])
        
        # Project next 6 months
        last_month = recent_data['headcount'].iloc[-1]
        forecast_months = pd.date_range(start=pd.to_datetime(recent_data['month'].iloc[-1]) + pd.DateOffset(months=1), 
                                        periods=6, freq='MS')
        
        forecast_values = [last_month + (i+1)*avg_monthly_change for i in range(6)]
        
        # Create forecast visualization
        plt.figure(figsize=(12, 6))
        
        # Plot historical data
        plt.plot(monthly_df['month'], monthly_df['headcount'], marker='o', linewidth=2, color=colors[0], label='Historical')
        
        # Plot forecast
        forecast_months_str = [d.strftime('%Y-%m') for d in forecast_months]
        plt.plot(forecast_months_str, forecast_values, marker='s', linewidth=2, linestyle='--', color=colors[4], label='Forecast')
        
        # Add shaded area for forecast uncertainty
        upper_bound = [val * 1.1 for val in forecast_values]
        lower_bound = [val * 0.9 for val in forecast_values]
        plt.fill_between(forecast_months_str, upper_bound, lower_bound, color=colors[4], alpha=0.2)
        
        plt.title('Staffing Forecast (Next 6 Months)', fontsize=16)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Projected Headcount', fontsize=12)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.legend()
        
        # Add annotation about attrition
        plt.annotate(f"Avg Monthly Attrition: {avg_attrition_rate:.2f}%\nProjected Hiring Need: {int(last_month * avg_attrition_rate/100 * 6)} (6 months)",
                    xy=(0.02, 0.02),
                    xycoords='axes fraction',
                    bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(images_dir / 'staffing_forecast.png', dpi=300, bbox_inches='tight')
        plt.close()

def analyze_optimal_hiring_time(monthly_df, images_dir):
    """Analyze the best time to start hiring based on historical patterns
    
    Args:
        monthly_df (pd.DataFrame): DataFrame with monthly staffing data
        images_dir (Path): Directory to save images
    """
    if monthly_df is None or len(monthly_df) < 12:
        logger.warning("Not enough data for seasonal hiring analysis")
        return
    
    # Extract month names and aggregate data by month
    monthly_df['month_name'] = pd.to_datetime(monthly_df['month']).dt.strftime('%b')
    month_analysis = monthly_df.groupby('month_name').agg({
        'joiners': 'mean',
        'leavers': 'mean',
        'attrition_rate': 'mean'
    }).reset_index()
    
    # Sort by calendar months
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_analysis['month_idx'] = month_analysis['month_name'].apply(lambda x: month_order.index(x))
    month_analysis = month_analysis.sort_values('month_idx')
    
    plt.figure(figsize=(12, 6))
    
    width = 0.35
    x = np.arange(len(month_analysis))
    
    plt.bar(x - width/2, month_analysis['joiners'], width, label='Avg Joiners', color='green')
    plt.bar(x + width/2, month_analysis['leavers'], width, label='Avg Leavers', color='red')
    
    # Add line for attrition rate
    ax2 = plt.twinx()
    ax2.plot(x, month_analysis['attrition_rate'], marker='o', color='blue', label='Attrition Rate (%)')
    ax2.set_ylabel('Attrition Rate (%)', fontsize=12, color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    plt.title('Seasonal Hiring and Attrition Patterns', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Average Employee Count', fontsize=12)
    plt.xticks(x, month_analysis['month_name'])
    plt.legend(loc='upper left')
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(images_dir / 'seasonal_hiring_pattern.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Calculate and identify the best months to hire (lowest attrition, highest joining rate)
    month_analysis['hiring_score'] = month_analysis['joiners'] - month_analysis['leavers']
    best_months = month_analysis.sort_values('hiring_score', ascending=False).head(3)['month_name'].tolist()
    worst_months = month_analysis.sort_values('hiring_score').head(3)['month_name'].tolist()
    
    return best_months, worst_months

def create_monthly_staffing_table(monthly_df):
    """Create HTML table with monthly staffing metrics
    
    Args:
        monthly_df (pd.DataFrame): DataFrame with monthly staffing data
        
    Returns:
        str: HTML table with monthly staffing metrics
    """
    if monthly_df is None or len(monthly_df) == 0:
        return "<p>No monthly staffing data available</p>"
    
    # Sort data by month (ascending)
    monthly_df = monthly_df.sort_values('month')
    
    # Format the table
    html_table = """
    <table class="staffing-table">
        <thead>
            <tr>
                <th>Month</th>
                <th>Headcount</th>
                <th>New Joiners</th>
                <th>Leavers</th>
                <th>Attrition Rate</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in monthly_df.iterrows():
        # Highlight high attrition cells
        attrition_class = ' class="high-attrition"' if row['attrition_rate'] > 5 else ''
        
        html_table += f"""
            <tr>
                <td>{row['month']}</td>
                <td>{row['headcount']}</td>
                <td>{row['joiners']}</td>
                <td>{row['leavers']}</td>
                <td{attrition_class}>{row['attrition_rate']}%</td>
            </tr>
        """
    
    html_table += """
        </tbody>
    </table>
    """
    
    return html_table
