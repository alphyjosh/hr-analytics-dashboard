# HR Analytics Dashboard - Deployment Guide

This guide will help you make your HR Analytics Dashboard accessible to anyone with a link. The application has been designed to be easily deployable to cloud platforms.

## Option 1: Deploy to Render (Recommended - Free & Easy)

[Render](https://render.com) provides free hosting for web applications and has excellent support for Python Flask apps.

1. **Create a Render account**
   - Sign up at [render.com](https://render.com)
   - No credit card required for basic hosting

2. **Deploy your application**
   - Click "New" and select "Web Service"
   - Connect your GitHub repository OR use the "Upload" option
   - Select the main branch of your repository
   - Use these settings:
     - **Name**: hr-analytics-dashboard (or your preferred name)
     - **Environment**: Python
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn hr_dashboard_web:app`

3. **Launch your application**
   - Click "Create Web Service"
   - Wait for deployment to complete (typically 2-5 minutes)
   - Your dashboard will be available at: `https://your-app-name.onrender.com`

## Option 2: Deploy to Railway

[Railway](https://railway.app) is another excellent platform with a generous free tier.

1. **Create a Railway account**
   - Sign up at [railway.app](https://railway.app)

2. **Deploy your application**
   - Create a new project
   - Select "Deploy from GitHub repo"
   - Configure environment variables:
     - `SECRET_KEY`: (leave blank, a secure key will be generated automatically)
   - Add the following service command:
     - `gunicorn hr_dashboard_web:app`

3. **Access your application**
   - Railway will provide a unique domain for your application
   - Share this link with anyone who needs access

## Option 3: Deploy to PythonAnywhere

[PythonAnywhere](https://www.pythonanywhere.com) offers a free plan suitable for hosting this application.

1. **Create a PythonAnywhere account**
   - Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload your files**
   - Use the Files tab to upload your project files
   - Or clone your repository using Bash console

3. **Set up a web app**
   - Go to the Web tab and click "Add a new web app"
   - Choose Flask and Python 3.9
   - Set the path to your application: `/home/yourusername/path/to/hr_dashboard_web.py`
   - Modify the WSGI file to import your app

## Customizing Your Organization's Data

Once deployed, anyone with the link can access and customize the dashboard:

1. **Accessing the dashboard**
   - Open the provided URL in any web browser
   - No login required - anyone with the link can access it

2. **Adding your organization's staffing data**
   - Click on "Edit Data" in the top navigation menu
   - You can either:
     - Modify the existing sample data entries
     - Add new months using the "Add Month" button
     - Remove months you don't need

3. **Required data for each month**
   - **Month**: Name or date identifier (e.g., "Jan 2025")
   - **Headcount**: Total number of staff at month end
   - **New Joiners**: Number of new employees that month
   - **Leavers**: Number of employees who left that month

4. **Setting your branding**
   - Click on "Branding" in the top navigation menu
   - Customize:
     - Company name
     - Dashboard title
     - Colors (primary and secondary)

## Data Persistence Notes

- The current implementation uses session storage
- Data will persist as long as the browser session is active
- For long-term data storage, you could enhance the app to:
  1. Use a database like SQLite or PostgreSQL
  2. Add a simple login system
  3. Add an export/import feature for data backup

## Getting Help

If you encounter any issues with deployment:

1. Check the logs on your hosting platform
2. Ensure all files were uploaded correctly
3. Verify that the requirements.txt file was included

For further assistance, please reach out for support.

---

**Note**: This application is configured to be publicly accessible to anyone with the link. If you need to restrict access, consider implementing user authentication.
