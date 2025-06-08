# HR Analytics Dashboard - Web Version

This web application provides an interactive HR Analytics Dashboard that tracks staffing levels and attrition rates over time. The application allows users to input their own staffing data, visualize trends, and export the results.

## Features

- **Monthly Staff Tracking**: Monitor headcount, new joiners, leavers, and attrition rates
- **Custom Data Input**: Add your organization's specific staffing values
- **Visual Analytics**: Interactive charts showing trends and patterns
- **Data Export**: Download your data in CSV format
- **Customizable Branding**: Set company name and color scheme
- **Headcount Forecasting**: Project future staffing needs based on trends

## Deployment Options

### Option 1: Deploy to Render (Free & Easy)

1. Create a free account at [render.com](https://render.com/)
2. Create a new Web Service
3. Connect your GitHub repository or upload the files directly
4. Set the following options:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn hr_dashboard_web:app`
5. Deploy the application
6. Share the provided URL with anyone who needs access

### Option 2: Deploy to Heroku

1. Create a free account at [heroku.com](https://heroku.com)
2. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. From your project directory, run:
   ```
   heroku login
   git init
   git add .
   git commit -m "Initial commit"
   heroku create hr-analytics-dashboard
   git push heroku master
   ```
4. Share the provided URL with your team

### Option 3: Deploy to PythonAnywhere (Free option available)

1. Create an account at [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Upload your files or clone your repository
3. Set up a new web app with Flask
4. Configure the WSGI file to point to your `hr_dashboard_web.py` file
5. Share the provided URL

## Local Development

To run the application locally:

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Flask application:
   ```
   python hr_dashboard_web.py
   ```

3. Access the dashboard at `http://localhost:5000`

## Customizing Your Data

1. Log into the deployed web application
2. Click "Edit Data" in the navigation menu
3. Modify the existing data or add new months
4. Click "Save Changes" to update the dashboard

## Important Notes

- The current version stores data in session memory, which means data will reset when the web server restarts
- For persistent storage in production, consider adding a database (SQLite, PostgreSQL, etc.)
- The application comes with sample data for demonstration purposes

## License

This project is available for personal and commercial use.

## Support

If you need assistance with deployment or customization, please reach out for support.
