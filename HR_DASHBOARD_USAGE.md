# Enhanced HR Analytics Dashboard - Usage Guide

## Overview

This enhanced HR Analytics Dashboard system generates comprehensive visualizations and metrics from your HR data, presenting them in a beautifully styled HTML dashboard. The system includes:

1. **Real data support**: Load HR data from CSV or Excel files
2. **Customizable branding**: Personalize colors, fonts, logo, and title
3. **Rich visualizations**: Multiple charts showing key HR metrics
4. **Scheduler**: Automatically regenerate dashboards on a regular basis
5. **Multiple output formats**: HTML dashboard with embedded images

## Requirements

Required Python packages:
```
pandas
numpy
matplotlib
seaborn
schedule
```

Install all required packages using:
```
pip install pandas numpy matplotlib seaborn schedule
```

## Files in this System

- `hr_analytics_real_data.py`: Handles data loading from files or generates sample data
- `hr_visualizations.py`: Creates visualization charts from HR data
- `hr_html_generator.py`: Provides styling and metrics calculation functions
- `hr_dashboard_main.py`: Main script integrating all components
- `branding_config_sample.json`: Sample configuration for dashboard appearance

## Quick Start

### Generate Dashboard with Sample Data

```
python hr_dashboard_main.py
```

This will:
1. Generate sample HR data
2. Create visualizations
3. Build an HTML dashboard
4. Open the dashboard in your default web browser

### Use Your Own HR Data

```
python hr_dashboard_main.py --data path/to/your/hr_data.csv
```

Your HR data file (CSV or Excel) should have these columns:
- `employee_id`: Unique identifier
- `age`: Employee age
- `gender`: Employee gender
- `department`: Employee department
- `position`: Job title
- `tenure`: Years at company
- `salary`: Annual salary
- `attrition`: 0 for active employees, 1 for those who left
- `satisfaction`: Job satisfaction rating (1-5)

Optional columns that enhance dashboard features:
- `work_life_balance`: Work-life balance rating (1-5)
- `performance_rating`: Performance rating (1-5)

### Customize Branding and Appearance

Create a JSON configuration file with your branding preferences (see `branding_config_sample.json`), then run:

```
python hr_dashboard_main.py --config your_branding_config.json
```

### Schedule Regular Dashboard Generation

For daily updates at 9:00 AM:

```
python hr_dashboard_main.py --schedule daily --time 09:00
```

For hourly updates:

```
python hr_dashboard_main.py --schedule hourly
```

For weekly updates on Monday at 9:00 AM:

```
python hr_dashboard_main.py --schedule weekly --time 09:00
```

Add your data file and branding configuration as needed:

```
python hr_dashboard_main.py --data your_data.csv --config your_brand.json --schedule daily --time 08:00
```

## Command Line Options

- `--data`: Path to your HR data CSV or Excel file
- `--config`: Path to branding configuration JSON file
- `--schedule`: Schedule type ('hourly', 'daily', 'weekly')
- `--time`: Time for scheduled generation (format: HH:MM)
- `--no-browser`: Disable automatic browser opening

## Output

All output is saved to the `hr_analytics_output` directory:
- `hr_dashboard.html`: Main dashboard file
- `images/`: Directory containing visualization images
- `hr_data.csv`: Sample data (if using generated data)

## Customizing Your Dashboard

### Brand Configuration

Edit the `branding_config_sample.json` file or create your own with these options:

```json
{
    "company_name": "Your Company Name",
    "logo_url": "path/to/your/logo.png",
    "primary_color": "#2c3e50",
    "secondary_color": "#e74c3c",
    "accent_color": "#3498db",
    "font_family": "Arial, sans-serif",
    "dashboard_title": "HR Analytics Dashboard - Your Company"
}
```

### Adding New Visualizations

To add new visualizations:
1. Add your new chart generation function in `hr_visualizations.py`
2. Save the output image to the `images_dir` directory
3. Update the HTML template in `hr_dashboard_main.py` to include the new image

## Troubleshooting

### Dashboard Not Opening Automatically
If the dashboard doesn't open automatically in your browser:
1. Check the console output for the dashboard file location
2. Open the HTML file manually in your preferred web browser

### Missing Data Columns
If your data file is missing required columns:
1. The system will use sample data for any missing columns
2. Check the console logs for warnings about missing columns

### Scheduler Not Running
If the scheduler doesn't seem to be working:
1. Ensure you have the `schedule` package installed
2. The script must be kept running for scheduled updates to occur
3. Use a system service or scheduled task to run the script if you need it to persist

## Future Enhancements

Planned future enhancements:
- Interactive charts with JavaScript visualization libraries
- Export to PDF functionality
- Email notifications with dashboard attachment
- Additional HR metrics and visualizations
- Integration with HR systems via APIs
