# HR Analytics Dashboard

A comprehensive HR analytics dashboard that provides insights into key HR metrics including employee turnover, recruitment effectiveness, and talent demographics.

## Features

- **Attrition Analysis**: Track and analyze employee turnover rates
- **Recruitment Metrics**: Monitor time-to-hire and source effectiveness
- **Diversity Dashboard**: Visualize workforce demographics and diversity metrics
- **Performance Analytics**: Analyze employee performance and engagement

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```
   streamlit run src/app.py
   ```

## Project Structure

```
hr-analytics-dashboard/
├── data/                   # Sample HR datasets
├── src/                    # Source code
│   ├── __init__.py
│   ├── app.py              # Main Streamlit application
│   ├── data_loader.py      # Data loading and preprocessing
│   └── visualizations.py   # Visualization components
├── .gitignore
├── requirements.txt
└── README.md
```

## Technologies Used

- Python
- Pandas & NumPy for data processing
- Plotly & Matplotlib for visualizations
- Streamlit for the web interface
