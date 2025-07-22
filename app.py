from flask import Flask, render_template, request, send_file, redirect, url_for, flash, jsonify
import pandas as pd
import os
import subprocess
from job_scraper import JobScraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime
from tkinter import Button
import threading
from flask import jsonify


app = Flask(__name__)
scraper = JobScraper()  # Initialize the scraper instance
scraping_status = {"running": False, "last_run": None}

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    

app.config.from_object(Config)


def fetch_api_jobs():
    """Fetch jobs from TheirStack API and return formatted data"""
    try:
        api_key = os.getenv('THEIRSTACK_API_KEY')
        
        if not api_key:
            print("Warning: THEIRSTACK_API_KEY not found in environment variables")
            return []

        payload = {
            "page": 0,
            "limit": 25,
            "job_country_code_or": ["KE"],
            "job_title_or": ["web developer"],
            "job_title_pattern_and": ["(?i)web developer"],
            "job_title_pattern_or": ["(?i)web developer"],
            "posted_at_max_age_days": 7
        }
 
        response = requests.post(f'https://api.theirstack.com/v1/jobs/search?token={api_key}', json=payload)

        
        if response.status_code == 200:
            api_data = response.json()
            jobs = api_data.get('data', [])
            
            # Format API jobs to match our Excel structure
            formatted_jobs = []
            for job in jobs:
                print(job)
                formatted_job = {
                  'Job Title':job['job_title'],
                  'Job Description': job['description'],
                  'Job Source': job['company'],
                  'Category': categorize_job(job['job_title']),
                  'Scraped Date': job['date_posted'],
                  'Job URL': job['url'],
                }
                formatted_jobs.append(formatted_job)
            
            return formatted_jobs
        else:
            print(f"API request failed with status code: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching API jobs: {str(e)}")
        return []


def categorize_job(job_title):
    """Categorize job based on title"""
    job_title_lower = job_title.lower()
    
    if any(keyword in job_title_lower for keyword in ['intern', 'internship']):
        return 'Internship'
    elif any(keyword in job_title_lower for keyword in ['junior', 'entry', 'beginner']):
        return 'Entry Level'
    elif any(keyword in job_title_lower for keyword in ['mobile', 'android', 'ios', 'react native']):
        return 'Mobile Development'
    elif any(keyword in job_title_lower for keyword in ['design', 'ui', 'ux', 'graphic']):
        return 'Design & Creative'
    elif any(keyword in job_title_lower for keyword in ['data', 'analyst', 'analytics']):
        return 'Data & Analytics'
    elif any(keyword in job_title_lower for keyword in ['content', 'writer', 'copywriter']):
        return 'Writing & Content'
    elif any(keyword in job_title_lower for keyword in ['manager', 'management', 'business']):
        return 'Business & Management'
    else:
        return 'Web Development'


@app.route('/api/jobs')
def api_jobs_endpoint():
    """API endpoint to return jobs data"""
    jobs = fetch_api_jobs()
    print(jobs)
    return jsonify(jobs)
    
@app.route('/')
def index():
    # Get scraped jobs from Excel file
    scraped_jobs = []
    excel_file = 'job_listings.xlsx'
    
    if os.path.exists(excel_file):
        try:
            df = pd.read_excel(excel_file)
            required_columns = ['Job Title', 'Job Description', 'Job Source', 'Category', 'Scraped Date', 'Job URL']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if not missing_columns:
                df = df.fillna('')
                # Filter out internships
                internship_categories = ['Internship', 'Web Development Internship', 'Beginner Internship']
                df = df[~df['Category'].isin(internship_categories)]
                
                # Add Source column if not present
                if 'Source' not in df.columns:
                    df['Source'] = 'Scraped'
                
                scraped_jobs = df.to_dict('records')
                
        except Exception as e:
            print(f"Error reading Excel file: {str(e)}")
    
    # Get API jobs
    api_jobs = fetch_api_jobs()
    
    # Combine both sources
    all_jobs = scraped_jobs + api_jobs
    
    # Convert to DataFrame for easier filtering
    if all_jobs:
        combined_df = pd.DataFrame(all_jobs)
        
        # Get filter parameters
        category = request.args.get('category', '')
        
        # Get all unique categories
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
            category = category.replace('&', 'and')
            combined_df = combined_df[combined_df['Category'].str.lower().str.contains(category.lower())]
        
        # Sort by scraped date (newest first)
        if 'Scraped Date' in combined_df.columns:
            combined_df = combined_df.sort_values('Scraped Date', ascending=False)
        
        final_jobs = combined_df.to_dict('records')
        
        # Get statistics
        total_jobs = len(combined_df)
        scraped_count = len([job for job in final_jobs if job.get('Source') == 'Scraped'])
        api_count = len([job for job in final_jobs if job.get('Source') == 'API'])
        
        # Get unique sources
        sources = combined_df['Job Source'].unique() if 'Job Source' in combined_df.columns else []
        
    else:
        final_jobs = []
        total_jobs = 0
        scraped_count = 0
        api_count = 0
        sources = []
        categories = []
        category = ''
    
    # Get internship statistics
    total_internships = 0
    try:
        if os.path.exists('internships.xlsx'):
            internship_df = pd.read_excel('internships.xlsx')
            internship_df = internship_df.fillna('')
            internship_categories = ['Internship', 'Web Development Internship', 'Beginner Internship']
            internship_df = internship_df[internship_df['Category'].isin(internship_categories)]
            total_internships = len(internship_df)
    except Exception as e:
        print(f"Error reading internships file: {str(e)}")
    
    return render_template('index.html', 
                         data=final_jobs,
                         total_jobs=total_jobs,
                         scraped_count=scraped_count,
                         api_count=api_count,
                         total_internships=total_internships,
                         sites=sources,
                         categories=categories,
                         selected_category=category,
                         download_link='/download',
                         error=None if all_jobs else 'No job listings found. Please run the scraper first or check your API configuration.')


@app.route('/scrape')
def start_scrape():
    try:
        # Check if already running (simple file-based check)
        if os.path.exists('scraping.lock'):
            flash('Scraping already in progress', 'info')
            return redirect(url_for('index'))
        
        # Create lock file
        with open('scraping.lock', 'w') as f:
            f.write('running')
        
        # Run in background thread
        thread = threading.Thread(target=background_scraper)
        thread.daemon = True
        thread.start()
        
        flash('Job scraping started in background!', 'success')
        
    except Exception as e:
        flash(f'Error starting scraper: {str(e)}', 'error')
        # Remove lock file if error
        if os.path.exists('scraping.lock'):
            os.remove('scraping.lock')
    
    return redirect(url_for('index'))

def background_scraper():
    try:
        result = subprocess.run(['python', 'job_scraper.py'],
                              capture_output=True, text=True, timeout=300)
        
        # Log result (since we can't flash from background thread)
        with open('scrape_log.txt', 'w') as f:
            if result.returncode == 0:
                f.write('success')
            else:
                f.write(f'failed: {result.stderr}')
                
    except subprocess.TimeoutExpired:
        with open('scrape_log.txt', 'w') as f:
            f.write('timeout')
    except Exception as e:
        with open('scrape_log.txt', 'w') as f:
            f.write(f'error: {str(e)}')
    finally:
        # Remove lock file
        if os.path.exists('scraping.lock'):
            os.remove('scraping.lock')

"""     if scraping_status["running"]:
        return jsonify({"error": "Scraping already in progress"}), 400
    
    # Start scraping in background thread
    thread = threading.Thread(target=run_scraper)
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Scraping started"}), 202

def run_scraper():
    scraping_status["running"] = True
    try:
        result = subprocess.run(['python', 'job_scraper.py'],
                              capture_output=True, text=True, timeout=300)
        # Store result in database or file
        scraping_status["last_run"] = "success" if result.returncode == 0 else "failed"
    except Exception as e:
        scraping_status["last_run"] = f"error: {str(e)}"
    finally:
        scraping_status["running"] = False

@app.route('/scrape/status')
def scrape_status():
    return jsonify(scraping_status) """
    
""" def scrape():
    try:
        # Run job scraper
        result = subprocess.run(['python', 'job_scraper.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            flash('Jobs updated successfully!', 'success')
        else:
            flash('Failed to update jobs', 'error')
            
    except subprocess.TimeoutExpired:
        flash('Job scraper timed out', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('index')) """
    

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
        categories = sorted(internships_df['Category'].unique()) if not internships_df.empty else []
        

        # Get statistics
        total_internships = len(internships_df)
        internships_by_category = internships_df['Category'].value_counts().to_dict() if not internships_df.empty else {}
        
        # Convert DataFrame to list of dictionaries for template
        internships_list = internships_df.to_dict('records') 
        
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
    """Download the Excel file with combined data"""
    try:
        # Get scraped jobs
        scraped_jobs = []
        excel_file = 'job_listings.xlsx'
        
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            df = df.fillna('')
            scraped_jobs = df.to_dict('records')
        
        # Get API jobs
        api_jobs = fetch_api_jobs()
        
        # Combine both sources
        all_jobs = scraped_jobs + api_jobs
        
        if all_jobs:
            # Create a new DataFrame with combined data
            combined_df = pd.DataFrame(all_jobs)
            
            # Save to a temporary file
            temp_file = 'combined_jobs.xlsx'
            combined_df.to_excel(temp_file, index=False)
            
            return send_file(
                temp_file,
                as_attachment=True,
                download_name='combined_jobs.xlsx'
            )
        else:
            return "No data available to download"
            
    except Exception as e:
        return f"Error creating download file: {str(e)}"

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