from flask import Flask, render_template, request, send_file, redirect
import pandas as pd
import os
from job_scraper import JobScraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime

app = Flask(__name__)
scraper = JobScraper()  # Initialize the scraper instance

@app.route('/')
def index():
    # Check if the Excel file exists
    excel_file = 'job_listings.xlsx'
    if not os.path.exists(excel_file):
        return render_template('index.html', data=None, error='No job listings found. Please run the scraper first.')
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        # Check if required columns exist
        required_columns = ['Job Title', 'Job Description', 'Job Source', 'Category', 'Scraped Date', 'Job URL']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return render_template('index.html', 
                                 data=None,
                                 error=f'Missing required columns in Excel file: {", ".join(missing_columns)}')
        
        # Fill NaN values with empty strings
        df = df.fillna('')
        
        # Filter out internships
        internship_categories = ['Internship', 'Web Development Internship', 'Beginner Internship']
        df = df[~df['Category'].isin(internship_categories)]
        
        # Get filter parameters
        category = request.args.get('category', '')
        
        # Get all unique categories excluding internships
        categories = [
            'All',
            'Entry Level',
            'Beginner Web Development',
            'Web Development',
            'Mobile Development',
            'Design & Creative',
            'Data & Analytics',
            'Writing & Content',
            'Business & Management'
        ]
        
        # Apply filters
        if category and category != 'All':
            # Handle special characters in category names
            category = category.replace('&', 'and')
            df = df[df['Category'].str.lower().str.contains(category.lower())]
        
        # Specify columns to display in the order we want
        columns_to_display = ['Job Title', 'Job Description', 'Job Source', 'Category', 'Scraped Date', 'Job URL']
        
        # Ensure all columns exist before displaying
        available_columns = [col for col in columns_to_display if col in df.columns]
        
        # Convert data to dictionary format for template
        data = df[available_columns].to_dict('records')
        
        # Get statistics
        total_jobs = len(df)
        sites = []
        if 'Source' in df.columns:
            sites = df['Source'].unique()
        
        # Get internship statistics (for display purposes)
        internship_df = pd.read_excel('internships.xlsx')  
        internship_df = internship_df.fillna('')  # Fill NaN values
        internship_categories = ['Internship', 'Web Development Internship', 'Beginner Internship']
        internship_df = internship_df[internship_df['Category'].isin(internship_categories)]
        total_internships = len(internship_df)

        return render_template('index.html', 
                             data=data,
                             total_jobs=total_jobs,
                             total_internships=total_internships,
                             sites=sites,
                             categories=categories,
                             selected_category=category,
                             download_link='/download')
    except Exception as e:
        return render_template('index.html', 
                             data=None,
                             error=f'Error reading Excel file: {str(e)}')


@app.route('/internships')
def internships():
    try:
        # Read the Excel file
        if not os.path.exists('internships.xlsx'):  
            return render_template('internships.html', 
                                 internships=[],
                                 categories=[],
                                 total_internships=0,
                                 internships_by_category={})
        
        df = pd.read_excel('internships.xlsx')  
        
        # Check if required columns exist
        required_columns = ['Job Title', 'Job Description', 'Job Source', 'Category', 'Scraped Date', 'Job URL']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return render_template('internships.html', 
                                 internships=[],
                                 categories=[],
                                 total_internships=0,
                                 internships_by_category={},
                                 error=f'Missing required columns in Excel file: {", ".join(missing_columns)}')
        
        # Fill NaN values with empty strings
        df = df.fillna('')
        
        # Filter for internships using Category
        #internship_categories = ['All', 'Entry Level', 'Beginner Web Development', 'Web Development', 'Mobile Development', 'Design & Creative', 'Data & Analytics', 'Writing & Content', 'Business & Management']
        internship_categories = ['Internship', 'Web Development Internship', 'Beginner Internship']
        internships_df = df[df['Category'].isin(internship_categories)]

         # Get filter parameters
        category = request.args.get('category', '')
        
        # Get all unique categories excluding internships
        categories = [
            'All',
            'Entry Level',
            'Beginner Web Development',
            'Web Development',
            'Mobile Development',
            'Design & Creative',
            'Data & Analytics',
            'Writing & Content',
            'Business & Management'
        ]
        
        # Apply filters
        if category and category != 'All':
            # Handle special characters in category names
            category = category.replace('&', 'and')
            internships_df = internships_df[internships_df['Category'].str.lower().str.contains(category.lower())]
        
        columns_to_display = ['Job Title', 'Job Description', 'Job Source', 'Category', 'Scraped Date', 'Job URL']
        
        # Ensure all columns exist before displaying
        available_columns = [col for col in columns_to_display if col in df.columns]
        
        # Convert data to dictionary format for template
        data = df[available_columns].to_dict('records')
        
        # Get statistics
        total_jobs = len(df)
        sites = []
        if 'Source' in df.columns:
            sites = df['Source'].unique()
        
        # Get internship statistics (for display purposes)
        internship_df = pd.read_excel('internships.xlsx')  
        internship_df = internship_df.fillna('')  # Fill NaN values
        internship_categories = ['Internship', 'Web Development Internship', 'Beginner Internship']
        internship_df = internship_df[internship_df['Category'].isin(internship_categories)]
        total_internships = len(internship_df)
 
        # Get unique categories
        """ categories = sorted(internships_df['Category'].unique()) if not internships_df.empty else []
        

        # Get statistics
        total_internships = len(internships_df)
        internships_by_category = internships_df['Category'].value_counts().to_dict() if not internships_df.empty else {}
        
        # Convert DataFrame to list of dictionaries for template
        internships_list = internships_df.to_dict('records') """
        
        return render_template(
            'internships.html',
            internships=internships_list,
            categories=categories,
            total_internships=total_internships,
            internships_by_category=internships_by_category,
            download_internships_link='/download_internships',
        )
    except Exception as e:
        return render_template('internships.html', 
                             internships=[],
                             categories=[],
                             total_internships=0,
                             internships_by_category={},
                             error=f'Error reading Excel file: {str(e)}')


@app.route('/download')
def download_excel():
    """Download the Excel file"""
    excel_file = 'job_listings.xlsx'
    if not os.path.exists(excel_file):
        return "No data available to download"
    
    return send_file(
        excel_file,
        as_attachment=True,
        download_name='freelance_jobs.xlsx'
    )

@app.route('/download_internships')
def download_internships():
    """Download Excel file containing only internship data"""
    excel_file = 'internships.xlsx'  
    if not os.path.exists(excel_file):
        return "No data available to download"

    return send_file(
        excel_file,
        as_attachment=True,
        download_name='internships.xlsx'
    )
    

if __name__ == '__main__':
    app.run(debug=True)
