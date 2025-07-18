from sys import intern
import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import re
from urllib.parse import urljoin

class JobScraper:
    def __init__(self):
        self.sites = {
            # Job boards
            'upwork': 'https://www.upwork.com/jobs/website-development/',
            'freelancer': 'https://www.freelancer.com/jobs/',
            'fiverr': 'https://www.fiverr.com/search/gigs?query=web+development',
            'wayup': 'https://www.wayup.com/jobs/computer/',
            'remoteok': 'https://remoteok.com/remote-jobs',
            'remotive': 'https://remotive.com/remote-jobs/software-dev?query=web%20development',
            'weworkremotely': 'https://weworkremotely.com/categories/remote-front-end-programming-jobs#job-listings',
            'pythonjobs': 'https://www.python.org/jobs/',
            'jobpresso': 'https://jobspresso.co/remote-work/',
            
            # Indeed URLs -add canada number to access obs from canada
            'indeed_jobs': 'https://www.indeed.com/jobs?q=web+developer&l=',
            'indeed_internships': 'https://www.indeed.com/jobs?q=web+developer+internship&sc=0kf%3Aattr%28DQF7BQF8YQFQ8DZQFQ%29%3B',
            
            # Glassdoor URLs
            'glassdoor_jobs': 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword=web+developer',
            'glassdoor_internships': 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword=web+developer+internship',
            
            # LinkedIn URLs
            'linkedin_jobs': 'https://www.linkedin.com/jobs/search/?keywords=web+developer',
            'linkedin_internships': 'https://www.linkedin.com/jobs/search/?currentJobId=4261958882&f_E=2&keywords=internship&origin=JOB_SEARCH_PAGE_JOB_FILTER',
            
            # add brighter monday
            'brightermonday_jobs': 'https://www.brightermonday.co.ke/jobs/web-development',
            'brightermonday_internships': 'https://www.brightermonday.co.ke/jobs/internship-graduate',
            
            # Internship-specific job boards
            #'letsintern': 'https://www.letsintern.com/internships/it-internships',
            'letsintern': 'https://www.letsintern.com/internships/online-virtual-internship',
            'internshala': 'https://internshala.com/internships/web+development+internship',
            'remoteok_internships':'https://remoteok.com/remote-jobs/internship',
            
            # Frontend/HTML/CSS/JS specific sources
            'g21': 'https://jobs.ashbyhq.com/g2i',
            #'g2i': 'https://www.g2i.co/frontend',  # Go2Intern - Frontend/Fullstack internships
            
            # Upwork internship
            'upwork_intern': 'https://www.upwork.com/jobs/internship/',
        }
        self.data = []
        self.internships = []
       

        self.categories = {
            'Web Development': [
                'web', 'website', 'frontend', 'backend', 'javascript', 'js', 'html', 'css',
                'bootstrap', 'jquery', 'react', 'angular', 'vue', 'node', 'php', 'laravel'
            ],
            'Mobile Development': [
                'mobile', 'ios', 'android', 'flutter', 'react native', 'swift', 'kotlin', 'xcode'
            ],
            'Design & Creative': [
                'design', 'graphic', 'ui', 'ux', 'edit', 'editing','editor','illustrator', 
                'photoshop', 'adobe', 'video', 'animation'
            ],
            'Writing & Content': [
                'writing', 'writer', 'content', 'copywriting', 'blog', 'article', 'seo', 'proofreading', 'translation'
            ],
            'Data & Analytics': [
                'data', 'analytics', 'analysis', 'python', 'r', 'sql', 'machine learning', 'ai', 'statistics'
            ],
            'Business & Management': [
                'business', 'management', 'consulting', 'strategy', 'marketing', 'sales', 'hr', 'operations'
            ]
        }
        self.web_dev_keywords = [
            # HTML/CSS/JavaScript terms
            'html', 'css', 'javascript', 'js',
            'web development', 'web developer', 'web designer',
            'front-end', 'frontend', 'front end',
            'client-side', 'user interface', 'ui',
            
            # Frameworks and libraries
            'bootstrap', 'react', 'tailwind',
            
            # Basic web development concepts
            'responsive design', 'cross-browser',
            'semantic html', 'css grid', 'flexbox',
            'dom manipulation', 'event handling',
            
            # Beginner/Starting role specific terms
            'beginner', 'entry level', 'junior', 'starter',
            'trainee', 'new to', 'learn as you go',
            'education', 'training', 'development program',
            'growth opportunity', 'career development',
            'junior developer', 'junior engineer',
            'entry-level developer', 'entry-level engineer',
            'web developer trainee', 'web developer intern',
            'web development trainee', 'web development intern',
            'frontend developer trainee', 'frontend developer intern',
            'html developer', 'css developer', 'javascript developer',
            'html css js developer', 'html css javascript developer',
            'web dev trainee', 'web dev intern',
            'web dev starter', 'web dev beginner',
            'starting role', 'starter role', 'beginner role',
            'entry position', 'junior position',
            'trainee position', 'starter position',
            'beginner position', 'entry-level position',
            'new to web development', 'learning web development',
            'web development beginner', 'web dev beginner',
            'html beginner', 'css beginner', 'javascript beginner',
            'front-end beginner', 'frontend beginner',
            'web development trainee', 'web dev trainee',
            'web development apprentice', 'web dev apprentice',
            'web development mentorship', 'web dev mentorship',
            'web development learning', 'web dev learning',
            'graduate', 'fresher', 'assistant', 'associate',
            'intern', 'internship', 'apprentice',
            'starting position', 'no experience required',
            'recent graduate', 'new grad',
            'open to freshers', 'software intern',
            'graduate software engineer', 'entry level software engineer',
            'junior frontend developer',
            'support engineer', 'tech support', 'IT intern',
           'web development intern'
        ]

        self.beginner_web_dev_keywords = [
            # HTML
            'html', 'html5', 'html basics', 'html fundamentals',
            'html structure', 'html tags', 'html elements',
            'html attributes', 'html forms', 'html tables',
            'html lists', 'html images', 'html links',
            'html headings', 'html paragraphs', 'html div',
            'html span', 'html semantic', 'html accessibility',
            
            # CSS
            'css', 'css3', 'css basics', 'css fundamentals',
            'css selectors', 'css properties', 'css values',
            'css units', 'css colors', 'css typography',
            'css layout', 'css positioning', 'css flexbox',
            'css grid', 'css animations', 'css transitions',
            'css transforms', 'css responsive',
            
            # JavaScript
            'javascript', 'js', 'javascript basics',
            'javascript fundamentals', 'js basics',
            'js fundamentals', 'javascript syntax',
            'javascript functions', 'javascript variables',
            'javascript arrays', 'javascript objects',
            'javascript loops', 'javascript conditions',
            'javascript events', 'javascript dom',
            'javascript api', 'javascript frameworks',
            
            # Beginner-level terms
            'beginner', 'entry level', 'junior', 'trainee',
            'fresh graduate', 'new to', 'learn', 'education',
            'training', 'first job', 'starter', 'starter role',
            'entry level role', 'junior role', 'trainee role',
            'internship role', 'intern role', 'student role',
            'graduate', 'fresher', 'assistant', 'associate',
            'intern', 'internship', 'apprentice',
            'starting position', 'no experience required',
            'recent graduate', 'new grad',
            'open to freshers',
            
            # Project-based learning
            'build website', 'create website', 'develop website',
            'website project', 'web project', 'frontend project',
            'practice project', 'learning project',
            'training project', 'internship project',
            'basic website', 'simple website',
            'beginner-friendly', 'entry-level',
            
            # Skills focus
            'html/css', 'css/html', 'javascript/html',
            'front-end fundamentals', 'basic web development',
            'web development basics', 'beginner web dev',
            'entry-level web dev', 'junior web dev',
            
            # Training terms
            'training program', 'learning program',
            'development program', 'growth program',
            'skill building', 'capacity building',
            'capacity development'
        ]

        self.internship_keywords = [
            # Direct internship terms
            'intern', 'internship', 'internships', 'internship opportunity',
            'internship applicant', 'intern applicant',
            'summer intern', 'fall intern', 'spring intern',
            'winter intern', 'academic year internship',
            'semester internship', 'academic internship',
            'student', 'graduate', 'undergraduate', 'college student',
            'academic program', 'academic position',
            'freshman', 'sophomore', 'junior', 'senior',
            'trainee', 'training', 'training program',
            'training role', 'training applicant',
            'co-op', 'cooperative', 'work-study',
            'practicum', 'apprenticeship', 'placement',
            'learning opportunity', 'professional development',
            'career development', 'industry experience',
            'internship program', 'student program',
            'education program', 'educational program',
            'learning program', 'development program',
            'growth program', 'skill building',
            'capacity building', 'capacity development',
            'student position', 'student role',
            'academic year', 'academic term',
            'school year', 'university year',
            'college year', 'academic semester',
            'academic quarter', 'academic period',
            'student training', 'student development',
            'student placement', 'student opportunity'
        ]

        self.non_internship_keywords = [
            # Full-time job terms
            'full-time', 'full time', 'permanent', 'permanent position',
            'permanent role', 'permanent employee',
            'long-term', 'long term', 'career position',
            'career opportunity', 'career role',
            
            # Contract terms
            'contract', 'contractor', 'contract position',
            'contract role', 'contract employee',
            
            # Freelance terms
            'freelance', 'freelancer', 'freelance position',
            'freelance role', 'freelance work',
            
            # Part-time terms
            'part-time', 'part time', 'part time position',
            'part time role', 'part time work',
            
            # Remote terms
            'remote', 'remote work', 'remote position',
            'remote role', 'remote employee',
            
            # Consultant terms
            'consultant', 'consultancy', 'consulting',
            'consultant position', 'consultant role',
            'consultant work',
            
            # Senior-level terms
            'senior', 'lead', 'principal', 'expert',
            'architect', 'manager', 'director',
            'chief', 'vp', 'vice president',
            
            # Advanced terms
            'advanced', 'senior level', 'expert level',
            'highly experienced', 'years of experience',
            'proven track record', 'extensive experience'
        ]

        self.beginner_keywords = [
            'beginner', 'entry level', 'junior', 'trainee', 'fresh graduate',
            'new to', 'learn', 'education', 'training', 'first job', 'starter',
            'student', 'recent graduate', 'no experience', 'entry-level',
            'learn as you go', 'entry position', 'starter role', 'entry-level',
            'junior web developer', 'entry level web developer',
            'frontend developer junior', 'web developer i',
            'associate web developer', 'trainee web developer',
            'web development intern', 'junior software engineer',
            'html css developer', 'ui developer entry level'
        ]
        
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def clean_text(self, text):
        """Clean text by removing newlines, extra whitespace, and invalid characters"""
        if not text:
            return "Not specified"
        try:
            # Remove newlines and extra whitespace
            text = str(text).strip()
            # Replace invalid characters
            text = ''.join(c for c in text if c.isprintable())
            # Truncate long text to avoid Excel cell size limits
            return text[:32767] if len(text) > 32767 else text
        except:
            return "Not specified"

    def get_customer_info(self, job):
        """Extract customer information from the job listing"""
        try:
            # Try to get customer name from Upwork
            customer_name = job.find('div', class_='identity-name')
            if customer_name:
                return self.clean_text(customer_name.text)
                
            # Try to get customer name from Freelancer
            customer_info = job.find('div', class_='JobSearchCard-primary-user')
            if customer_info:
                return self.clean_text(customer_info.text)
                
            return "Anonymous Employer"
        except:
            return "Anonymous Employer"

    def get_category(self, title, description):
        """Determine job category based on keywords in both title and description"""
        text = f"{title.lower()} {description.lower()}"
        
        # First check for non-internship keywords (exclude full-time positions)
        if any(keyword in text for keyword in self.non_internship_keywords):
            return "Other"
            
        # Check for internship keywords first
        if any(keyword in text for keyword in self.internship_keywords):
            # Check if it's related to web development
            if any(keyword in text for keyword in self.web_dev_keywords):
                return "Web Development Internship"
            elif any(keyword in text for keyword in self.beginner_web_dev_keywords):
                return "Beginner Internship"
            return "Internship"
            
        # Check for web development keywords
        if any(keyword in text for keyword in self.web_dev_keywords):
            # Check if it's a beginner position
            if any(keyword in text for keyword in self.beginner_web_dev_keywords):
                return "Beginner Web Development"
            return "Web Development"
            
        # Check for beginner/entry-level keywords
        if any(keyword in text for keyword in self.beginner_keywords):
            return "Entry Level"
            
        # Check for category keywords
        for category, keywords in self.categories.items():
            if any(keyword in text for keyword in keywords):
                return category
                
        return "Other"
    
    """ def fetch_jobs(self):
        api_key = os.getenv('THEIRSTACK_API_KEY')

        payload = {
            "page": 0,
            "limit": 25,
            "job_country_code_or": [
                "KE"
            ],
            "job_title_or": [
                "web developer"
            ],
            "job_title_pattern_and": [
                "(?i)web developer"
            ],
            "job_title_pattern_or": [
                "(?i)web developer"
            ],
            "posted_at_max_age_days": 7
        }

        api_jobs = requests.post(f'https://api.theirstack.com/v1/jobs/search?token={api_key}', json=payload)

        for api_job in api_jobs.json():
            for data in api_job: 
            self.data.append({
                            'Job Title':api_job.job_title,
                            'Job Description': api_job.description,
                            'Job Source': api_job.company,
                            #'Category': self.get_category(api_job.title, api_job.description),
                            'Job URL': api_job.source_url,
                        })
        print(f'API_JOBS: {api_jobs.json()}')
        return api_jobs.json() """


    def scrape_indeed(self, is_internship=True):
        """Scrape web development jobs or internships from Indeed"""
        print(f"Scraping Indeed {'internships' if is_internship else 'jobs'}...")
        try:
            url = self.sites['indeed_internships' if is_internship else 'indeed_jobs']
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            jobs = soup.find_all('div', class_='job_seen_beacon')
            for job in jobs[0:31]:
                title = self.clean_text(job.find('h2').text)
                company = self.clean_text(job.find('span', class_='companyName').text)
                description = self.clean_text(job.find('div', class_='job-snippet').text)
                job_url = urljoin('https://www.indeed.com', job.find('a')['href'])
                
                # Skip if not web development related
                if not any(keyword in description.lower() for keyword in self.web_dev_keywords):
                    continue
                    
                # For internships, check internship keywords
                if is_internship:
                    if not any(keyword in description.lower() for keyword in self.internship_keywords):
                        continue
                
                # Skip if it's not beginner level
                if not any(keyword in description.lower() for keyword in self.beginner_web_dev_keywords):
                    continue
                
                self.data.append({
                    'Job Title': title,
                    'Job Description': description,
                    'Job Source': 'Indeed',
                    'Category': self.get_category(title, description),
                    'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Job URL': job_url
                })
        except Exception as e:
            print(f"Error scraping Indeed {'internships' if is_internship else 'jobs'}: {str(e)}")

    def scrape_linkedin(self, is_internship=True):
        driver = None
        """Scrape web development jobs or internships from LinkedIn"""
        print(f"Scraping LinkedIn {'internships' if is_internship else 'jobs'}...")
        try:
            driver = self.setup_driver()
            url = self.sites['linkedin_internships' if is_internship else 'linkedin_jobs']
            driver.get(url)
            time.sleep(5)
            
            jobs = driver.find_elements(By.CSS_SELECTOR, '.job-card-container')
            for job in jobs[0:31]:
                title = self.clean_text(job.find_element(By.CSS_SELECTOR, '.job-card-container__link').text)
                company = self.clean_text(job.find_element(By.CSS_SELECTOR, 'ltr').get_attribute('dir').text)
                #description = self.clean_text(job.find_element(By.CSS_SELECTOR, '.job-card-description').text)
                job_url = urljoin('https://www.linkedin.com', job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'))
                
                # Skip if not web development related
                if not any(keyword in title.lower() for keyword in self.web_dev_keywords):
                    continue
                    
                # For internships, check internship keywords
                if is_internship:
                    if not any(keyword in title.lower() for keyword in self.internship_keywords):
                        continue
                
                self.data.append({
                    'Job Title': title,
                   # 'Job Description': description,
                    'Job Source': 'LinkedIn',
                    'Category': self.get_category(title, company),
                    'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Job URL': job_url
                })
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping LinkedIn {'internships' if is_internship else 'jobs'}: {str(e)}")

    def scrape_glassdoor(self, is_internship=True):
        driver = None
        """Scrape web development jobs or internships from Glassdoor"""
        print(f"Scraping Glassdoor {'internships' if is_internship else 'jobs'}...")
        try:
            driver = self.setup_driver()
            url = self.sites['glassdoor_internships' if is_internship else 'glassdoor_jobs']
            driver.get(url)
            time.sleep(5)
            
            jobs = driver.find_elements(By.CSS_SELECTOR, '.job-listings .react-job-listing')
            for job in jobs[0:31]:
                title = self.clean_text(job.find_element(By.CSS_SELECTOR, '.jobTitle').text)
                company = self.clean_text(job.find_element(By.CSS_SELECTOR, '.jobCompany').text)
                description = self.clean_text(job.find_element(By.CSS_SELECTOR, '.jobDescriptionContent').text)
                job_url = urljoin('https://www.glassdoor.com', job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'))
                
                # Skip if not web development related
                if not any(keyword in description.lower() for keyword in self.web_dev_keywords):
                    continue
                    
                # For internships, check internship keywords
                if is_internship:
                    if not any(keyword in description.lower() for keyword in self.internship_keywords):
                        continue
                
                self.data.append({
                    'Job Title': title,
                    'Job Description': description,
                    'Job Source': 'Glassdoor',
                    'Category': self.get_category(title, description),
                    'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Job URL': job_url
                })
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Glassdoor {'internships' if is_internship else 'jobs'}: {str(e)}")

    def scrape_upwork(self):
        driver = None
        """Scrape job listings from Upwork"""
        try:
            driver = self.setup_driver()
            driver.get(self.sites['upwork'])
            time.sleep(5)
            
            # Wait for job elements to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'job-tile-title'))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('div', class_='job-tile')
            
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('h3', class_='job-tile-title')
                    description_elem = job.find('div', class_='job-description')
                    
                    if title_elem and description_elem:
                        # Get job URL
                        job_url = None
                        if title_elem.find('a'):
                            job_url = self.sites['upwork'] + title_elem.find('a')['href']
                        else:
                            job_url = "Not specified"
                        
                        title = self.clean_text(title_elem.text)
                        description = self.clean_text(description_elem.text)
                        
                        self.data.append({
                            'Job Title': title,
                            'Job Description': description,
                            'Job Source': 'Upwork',
                            'Category': self.get_category(title, description),
                            'Job URL': job_url,
                            'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error processing Upwork job: {e}")
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Upwork: {e}")

    def scrape_upwork_intern(self):
        driver = None
        """Scrape internship job listings from Upwork"""
        try:
            driver = self.setup_driver()
            driver.get(self.sites['upwork_intern'])
            time.sleep(5)
            
            # Wait for job elements to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'job-tile-title'))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            internships = soup.find_all('div', class_='job-tile')
            
            for internship in internships[0:31]:
                try:
                    title_elem = internship.find('h3', class_='job-tile-title')
                    description_elem = internship.find('div', class_='job-description')
                    
                    if title_elem and description_elem:
                        # Get job URL
                        job_url = None
                        if title_elem.find('a'):
                            job_url = self.sites['upwork_intern'] + title_elem.find('a')['href']
                        else:
                            job_url = "Not specified"
                        
                        title = self.clean_text(title_elem.text)
                        description = self.clean_text(description_elem.text)
                        
                        self.internships.append({
                            'Job Title': title,
                            'Job Description': description,
                            'Job Source': 'Upwork Internship',
                            'Category': self.get_category(title, description),
                            'Job URL': job_url,
                            'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error processing Upwork internship job: {e}")
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Upwork internship: {e}")

    def scrape_freelancer(self):
        driver = None
        """Scrape job listings from Freelancer"""
        try:
            driver = self.setup_driver()
            driver.get(self.sites['freelancer'])
            time.sleep(5)
            
            # Wait for job elements to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.JobSearchCard-primary-heading'))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('div', class_='JobSearchCard-item')
            
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('a', class_='JobSearchCard-primary-heading-link')
                    description_elem = job.find('p', class_='JobSearchCard-primary-description')
                    
                    if title_elem and description_elem:
                        # Get job URL
                        job_url = None
                        if title_elem.get('href'):
                            # Get the full URL from the href
                            relative_url = title_elem['href']
                            # Clean the URL
                            if relative_url:
                                # Remove any redirect parameters
                                if '?' in relative_url:
                                    relative_url = relative_url.split('?')[0]
                                # Handle project URL pattern
                                if '/projects/' in relative_url:
                                    # Clean up any duplicate /projects/ in URL
                                    relative_url = relative_url.replace('//projects/', '/projects/')
                                    # Get the project ID from URL
                                    project_id_match = re.search(r'/projects/\d+', relative_url)
                                    if project_id_match:
                                        job_url = f"https://www.freelancer.com{relative_url}"
                                    else:
                                        # If no project ID found, construct URL
                                        job_url = f"https://www.freelancer.com{relative_url}"
                                # Handle specific redirect patterns
                                elif '/jobs/1/' in relative_url:
                                    # Extract job ID from URL
                                    job_id_match = re.search(r'/jobs/1/(\d+)', relative_url)
                                    if job_id_match:
                                        job_id = job_id_match.group(1)
                                        job_url = f"https://www.freelancer.com/projects/{job_id}"
                                    else:
                                        # If we can't extract job ID, use the full URL
                                        relative_url = relative_url.replace('/jobs/1/', '/projects/')
                                        job_url = self.sites['freelancer'] + relative_url
                                elif '/jobs/' in relative_url:
                                    # Extract job ID from URL
                                    job_id_match = re.search(r'/jobs/(\d+)', relative_url)
                                    if job_id_match:
                                        job_id = job_id_match.group(1)
                                        job_url = f"https://www.freelancer.com/projects/{job_id}"
                                    else:
                                        # If we can't extract job ID, use the full URL
                                        relative_url = relative_url.replace('/jobs/', '/projects/')
                                        job_url = self.sites['freelancer'] + relative_url
                                elif '/job/' in relative_url:
                                    # Extract job ID from URL
                                    job_id_match = re.search(r'/job/(\d+)', relative_url)
                                    if job_id_match:
                                        job_id = job_id_match.group(1)
                                        job_url = f"https://www.freelancer.com/projects/{job_id}"
                                    else:
                                        # If we can't extract job ID, use the full URL
                                        relative_url = relative_url.replace('/job/', '/projects/')
                                        job_url = self.sites['freelancer'] + relative_url
                                else:
                                    # For any other URL, just use it as is
                                    job_url = self.sites['freelancer'] + relative_url
                        else:
                            job_url = "Not specified"
                        
                        title = self.clean_text(title_elem.text)
                        description = self.clean_text(description_elem.text)
                        
                        self.data.append({
                            'Job Title': title,
                            'Job Description': description,
                            'Job Source': 'Freelancer',
                            'Category': self.get_category(title, description),
                            'Job URL': job_url,
                            'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error processing Freelancer job: {e}")
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Freelancer: {e}")

    def scrape_jobpresso(self):
        driver = None
        """Scrape job listings from Jobpresso"""
        try:
            driver = self.setup_driver()
            driver.get(self.sites['jobpresso'])
            time.sleep(5)
            
            """ <a href="https://jobspresso.co/job/sanctuary-computer-us-or-located-between-pacific-standard-time-utc-8-and-central-european-time-utc2-designer-developer-marketing-various-product-mgmt-sales-senior-lead-account/" class="job_listing-clickbox"></a> """
            # Wait for job elements to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.job_listing-clickbox'))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('a', class_='job_listing-clickbox')
            
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('h3', class_='job_listing-title')
                    description_elem = job.find('span', class_='job_listing-company-tagline')
                    
                    if title_elem and description_elem:
                        # Get job URL
                        job_url = None
                        if job.get('href'):
                            # Get the full URL from the href
                            relative_url = job['href']
                            # Clean the URL
                            if relative_url:
                                # Remove any redirect parameters
                                if '?' in relative_url:
                                    relative_url = relative_url.split('?')[0]
                                # Handle project URL pattern
                                if '/projects/' in relative_url:
                                    # Clean up any duplicate /projects/ in URL
                                    relative_url = relative_url.replace('//projects/', '/projects/')
                                    # Get the project ID from URL
                                    project_id_match = re.search(r'/projects/\d+', relative_url)
                                    if project_id_match:
                                        job_url = f"https://www.jobspresso.co/remote-work/{relative_url}"
                                    else:
                                        # If no project ID found, construct URL
                                        job_url = f"https://www.jobspresso.co/remote-work/{relative_url}"
                                # Handle specific redirect patterns
                                elif '/jobs/1/' in relative_url:
                                    # Extract job ID from URL
                                    job_id_match = re.search(r'/jobs/1/(\d+)', relative_url)
                                    if job_id_match:
                                        job_id = job_id_match.group(1)
                                        job_url = f"https://www.jobspresso.co/remote-work/{job_id}"
                                    else:
                                        # If we can't extract job ID, use the full URL
                                        relative_url = relative_url.replace('/jobs/1/', '/projects/')
                                        job_url = self.sites['jobpresso'] + relative_url
                                elif '/jobs/' in relative_url:
                                    # Extract job ID from URL
                                    job_id_match = re.search(r'/jobs/(\d+)', relative_url)
                                    if job_id_match:
                                        job_id = job_id_match.group(1)
                                        job_url = f"https://www.jobspresso.co/remote-work/{job_id}"
                                    else:
                                        # If we can't extract job ID, use the full URL
                                        relative_url = relative_url.replace('/jobs/', '/projects/')
                                        job_url = self.sites['jobpresso'] + relative_url
                                elif '/job/' in relative_url:
                                    # Extract job ID from URL
                                    job_id_match = re.search(r'/job/(\d+)', relative_url)
                                    if job_id_match:
                                        job_id = job_id_match.group(1)
                                        job_url = f"https://www.jobspresso.co/remote-work/{job_id}"
                                    else:
                                        # If we can't extract job ID, use the full URL
                                        relative_url = relative_url.replace('/job/', '/projects/')
                                        job_url = self.sites['jobpresso'] + relative_url
                                else:
                                    # For any other URL, just use it as is
                                    job_url = self.sites['jobpresso'] + relative_url
                        else:
                            job_url = "Not specified"
                        
                        title = self.clean_text(title_elem.text)
                        description = self.clean_text(description_elem.text)
                        
                        self.data.append({
                            'Job Title': title,
                            'Job Description': description,
                            'Job Source': 'Jobpresso',
                            'Category': self.get_category(title, description),
                            'Job URL': job_url,
                            'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error processing Jobpresso job: {e}")
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Jobpresso: {e}")
            
    def scrape_pythonjobs(self):
        driver = None
        """Scrape job listings from Python Jobs"""
        try:
            driver = self.setup_driver()
            driver.get(self.sites['pythonjobs'])
            time.sleep(5)
            
            # Wait for job elements to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.listing-company-name'))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('span', class_='listing-company-name')
            
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('span', class_='listing-company-name')
                    """ description_elem = job.find('span', class_='listing-company-name') """
                    
                    if title_elem:
                        # Get job URL
                        job_url = None
                        if title_elem.find('a'):
                            job_url = self.sites['pythonjobs'] + title_elem.find('a')['href']
                        else:
                            job_url = "Not specified"
                        
                        title = self.clean_text(title_elem.text)
                        """ description = self.clean_text(description_elem.text) """
                        
                        self.data.append({
                            'Job Title': title,
                            """ 'Job Description': description, """
                            'Job Source': 'Python Jobs',
                            'Category': self.get_category(title, description),
                            'Job URL': job_url,
                            'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error processing Python Jobs job: {e}")
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Python Jobs: {e}")
            

    def scrape_remoteok(self):
        driver = None
        """Scrape job listings from Remote OK"""
        print("Scraping Remote OK jobs...")
        try:
            driver = self.setup_driver()
            print(f"Visiting URL: {self.sites['remoteok']}")
            driver.get(self.sites['remoteok'])
            time.sleep(5)
            
            # Wait for job elements to be present
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.preventLink'))
                )
                print("Found job elements")
            except Exception as e:
                print(f"Error waiting for job elements: {str(e)}")
                print("Page source:")
                print(driver.page_source[:1000])  # Print first 1000 chars of page source
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('a', class_='preventLink')
            print(f"Found {len(jobs)} job elements")
            
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('h2')
                    if title_elem:
                        print(f"Found job title: {title_elem.text}")
                    else:
                        print("No title element found")
                        continue
                        
                    title = self.clean_text(title_elem.text)
                    
                    # Get job URL
                    job_url = None
                
                    if job.get('href'):
                        # Clean the URL
                        relative_url = job['href']
                        if relative_url:
                            # Handle external URLs
                            if relative_url.startswith('http') or relative_url.startswith('https'):
                                job_url = relative_url
                            else:
                                # Handle internal URLs
                                job_url = urljoin('https://remoteok.com', relative_url)
                                # Clean URL parameters
                                if '?' in job_url:
                                    job_url = job_url.split('?')[0]
                                # Remove trailing slash if present
                                if job_url.endswith('/'):
                                    job_url = job_url.rstrip('/')
                    else:
                        job_url = '#'  # Fallback URL
                    
                    self.data.append({
                        'Job Title': title,
                        'Job Source': 'Remote OK',
                        'Category': self.get_category(title, ""),
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Job URL': job_url
                    })
                    print(f"Added job: {title}")
                except Exception as e:
                    print(f"Error processing Remote OK job: {str(e)}")
                    continue
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Remote OK: {str(e)}")
            if driver:
                driver.quit()

    def scrape_g21(self):
        """Scrape job listings from G21"""
        print("Scraping G21 jobs...")
        driver = None
        try:
            driver = self.setup_driver()
            print(f"Visiting URL: {self.sites['g21']}")
            driver.get(self.sites['g21'])
        
            # Wait longer for the page to load
            time.sleep(10)
        
            # Wait for job container to be present - try multiple selectors
            job_container_found = False
            selectors_to_try = [
            (By.CLASS_NAME, "ashby-job-posting-brief-list"),
            (By.CSS_SELECTOR, "[class*='ashby-job-posting-brief-list']"),
            (By.CSS_SELECTOR, "div[class*='container']"),
            (By.TAG_NAME, "main"),
            (By.CSS_SELECTOR, "a[href*='/g2i/']")
            ]
        
            for selector_type, selector_value in selectors_to_try:
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    print(f"Found elements with selector: {selector_value}")
                    job_container_found = True
                    break
                except Exception as e:
                    print(f"Selector {selector_value} failed: {str(e)}")
                    continue
        
            if not job_container_found:
                print("No job container found with any selector")
                print("Page source:")
                print(driver.page_source[:2000])
                return
        
            # Additional wait for dynamic content
            time.sleep(5)
        
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        
            # Try multiple approaches to find jobs
            jobs = []
        
            # Method 1: Look for the job container first
            job_container = soup.find('div', class_='ashby-job-posting-brief-list')
            if job_container:
                jobs = job_container.find_all('a', href=True)
            print(f"Method 1: Found {len(jobs)} jobs in container")
        
            # Method 2: Look for any links containing '/g2i/'
            if not jobs:
                jobs = soup.find_all('a', href=lambda x: x and '/g2i/' in x)
                print(f"Method 2: Found {len(jobs)} jobs with /g2i/ links")
        
            # Method 3: Look for elements with job-related classes
            if not jobs:
                jobs = soup.find_all('a', class_=lambda x: x and 'container' in str(x))
                print(f"Method 3: Found {len(jobs)} jobs with container class")
        
            # Method 4: Look for any elements with job titles
            if not jobs:
                title_elements = soup.find_all('h3', class_=lambda x: x and 'title' in str(x))
                jobs = [elem.find_parent('a') for elem in title_elements if elem.find_parent('a')]
                jobs = [job for job in jobs if job is not None]
                print(f"Method 4: Found {len(jobs)} jobs via title elements")
        
            if not jobs:
                print("No jobs found with any method")
                print("Available links on page:")
                all_links = soup.find_all('a', href=True)
                for link in all_links[:10]:  # Show first 10 links
                    print(f"  {link.get('href')} - {link.get_text(strip=True)[:50]}")
                return
        
            print(f"Processing {len(jobs)} job elements")
        
            for job in jobs[0:31]:
                try:
                    # Find the job title - try multiple selectors
                    title = None
                    title_elem = None
                    
                    title_selectors = [
                        ('h3', 'ashby-job-posting-brief-title'),
                        ('h3', lambda x: x and 'title' in str(x)),
                        ('h3', None),
                    ]
                
                    for tag, class_name in title_selectors:
                        if class_name:
                            if callable(class_name):
                                title_elem = job.find(tag, class_=class_name)
                            else:
                                title_elem = job.find(tag, class_=class_name)
                        else:
                            title_elem = job.find(tag)
                    
                        if title_elem:
                            title = self.clean_text(title_elem.text)
                            print(f"Found job title: {title}")
                            break
                
                    if not title:
                        # Try to get text from the link itself
                        title_text = job.get_text(strip=True)
                        if title_text and len(title_text) > 5:
                            # Extract just the first line or first 100 chars
                            title_lines = title_text.split('\n')
                            title = self.clean_text(title_lines[0][:100])
                            print(f"Using link text as title: {title}")
                        else:
                            print("No title found, skipping")
                            continue
                
                    # Get job URL
                    job_url = None
                    if job.get('href'):
                        relative_url = job['href']
                        if relative_url:
                            # Handle relative URLs
                            if relative_url.startswith('/'):
                                job_url = urljoin('https://jobs.ashbyhq.com', relative_url)
                            elif relative_url.startswith('http'):
                                job_url = relative_url
                            else:
                                job_url = urljoin('https://jobs.ashbyhq.com/g2i/', relative_url)
                    else:
                        job_url = '#'  # Fallback URL
                
                    # Extract additional details (location, type, etc.)
                    details_elem = job.find('div', class_='ashby-job-posting-brief-details')
                    location = ""
                    job_type = ""
                
                    if details_elem:
                        details_text = details_elem.get_text(strip=True)
                        # Extract job type (Full time, Contract, etc.)
                    if "Full time" in details_text:
                        job_type = "Full time"
                    elif "Contract" in details_text:
                        job_type = "Contract"
                    elif "Part time" in details_text:
                        job_type = "Part time"
                    
                    # Extract location info (Remote is mentioned)
                    if "Remote" in details_text:
                        location = "Remote"
                
                    self.data.append({
                    'Job Title': title,
                    'Job Source': 'G21',
                    'Location': location,
                    'Job Type': job_type,
                    'Category': self.get_category(title, ""),
                    'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Job URL': job_url
                    })
                    print(f"Added job: {title}")
                
                except Exception as e:
                    print(f"Error processing G21 job: {str(e)}")
                    continue
        
            print(f"Successfully scraped {len([d for d in self.data if d['Job Source'] == 'G21'])} jobs from G21")
        
        except Exception as e:
            print(f"Error scraping G21: {str(e)}")
        finally:
            if driver:
                driver.quit()

    def scrape_remotive(self):
        driver = None
        """Scrape job listings from Remotive"""
        print("Scraping Remotive jobs...")
        try:
            driver = self.setup_driver()
            print(f"Visiting URL: {self.sites['remotive']}")
            driver.get(self.sites['remotive'])
            time.sleep(5)
            
            # Wait for job elements to be present
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.remotive-url-visit'))
                )
                print("Found job elements")
            except Exception as e:
                print(f"Error waiting for job elements: {str(e)}")
                print("Page source:")
                print(driver.page_source[:1000])  # Print first 1000 chars of page source
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('a', class_='remotive-url-visit')
            print(f"Found {len(jobs)} job elements")
            
            """    title_elem = job.find('a', class_='JobSearchCard-primary-heading-link')
                    description_elem = job.find('p', class_='JobSearchCard-primary-description')
                    
                    if title_elem and description_elem:
                        # Get job URL
                        job_url = None
                        if title_elem.get('href'):
                            # Get the full URL from the href
                            relative_url = title_elem['href'] """
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('span')
                    if title_elem:
                        print(f"Found job title: {title_elem.text}")
                    else:
                        print("No title element found")
                        continue
                        
                    title = self.clean_text(title_elem.text)
                    
                    job_url = None
                    # Get job URL
                    if job.get('href'):
                        # Clean the URL
                        relative_url = job['href']
                        if relative_url:
                            # Handle external URLs
                            if relative_url.startswith('http') or relative_url.startswith('https'):
                                job_url = relative_url
                            else:
                                # Handle internal URLs
                                job_url = urljoin('https://remotive.com/remote-jobs', relative_url)
                                # Clean URL parameters
                                if '?' in job_url:
                                    job_url = job_url.split('?')[0]
                                # Remove trailing slash if present
                                if job_url.endswith('/'):
                                    job_url = job_url.rstrip('/')
                    else:
                        job_url = '#'  # Fallback URL
                    
                    self.data.append({
                        'Job Title': title,
                        'Job Source': 'Remotive',
                        'Category': self.get_category(title, ""),
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Job URL': job_url
                    })
                    print(f"Added job: {title}")
                except Exception as e:
                    print(f"Error processing Remotive job: {str(e)}")
                    continue
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Remotive: {str(e)}")
            if driver:
                driver.quit()
    
    def scrape_weworkremotely(self):
        driver = None
        """Scrape job listings from We Work Remotely"""
        print("Scraping We Work Remotely jobs...")
        try:
            driver = self.setup_driver()
            print(f"Visiting URL: {self.sites['weworkremotely']}")
            driver.get(self.sites['weworkremotely'])
            time.sleep(5)

            #<h4 class="new-listing__header__title"> Senior React Native Developer </h4>
            
            # Wait for job elements to be present
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '/listings/proxify-ab-senior-react-native-developer-3'))
                )
                print("Found job elements")
            except Exception as e:
                print(f"Error waiting for job elements: {str(e)}")
                print("Page source:")
                print(driver.page_source[:1000])  # Print first 1000 chars of page source
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('h4', class_='new-listing__header__title')
            print(f"Found {len(jobs)} job elements")
            
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('h4', class_='new-listing__header__title')
                    if title_elem:
                        print(f"Found job title: {title_elem.text}")
                    else:
                        print("No title element found")
                        continue
                        
                    title = self.clean_text(title_elem.text)
                    
                    """ if job.get('href'):
                        # Clean the URL
                        relative_url = job['href']
                        if relative_url:
                            # Handle external URLs
                            if relative_url.startswith('http') or relative_url.startswith('https'):
                                job_url = relative_url
                            else:
                                # Handle internal URLs
                                job_url = urljoin('https://remoteok.com', relative_url)
                                # Clean URL parameters
                                if '?' in job_url:
                                    job_url = job_url.split('?')[0]
                                # Remove trailing slash if present
                                if job_url.endswith('/'):
                                    job_url = job_url.rstrip('/')
                    else:
                        job_url = '#'  # Fallback URL """
                    """ <a href="/listings/proxify-ab-senior-react-native-developer-3"><div class=" new-listing paid-logo "><div class="new-listing__header"><h4 class="new-listing__header__title"> Senior React Native Developer </h4><div class=" new-listing__header__icons "><p class="new-listing__header__icons__date"> 4d </p><img alt="Pin Icon" class="new-listing__header__icons__pinnedIcon" src="https://weworkremotely.com/assets/pin-new-listing-icon-f1eb7ca3238f0782d024b085847f32a6b73b7de1e011e877855c0525cb7b87e5.svg"></div></div><p class="new-listing__company-name"> Proxify AB <img alt="Star Icon" class="lis-container__job__sidebar__companyDetails__info__title__icon" src="https://weworkremotely.com/assets/company-name-new-listing-icon-1535d75c2a56fe22cf7821636a862de6f5dcb83b1395dc2c164b77476b274c99.svg"></p><p class="new-listing__company-headquarters"> Sweden <i class="fa-solid fa-location-dot" aria-hidden="true"></i></p><div class="new-listing__categories"><p class="new-listing__categories__category new-listing__categories__category--featured">Featured</p><p class="new-listing__categories__category new-listing__categories__category--top-company"><i class="fa-regular fa-star" aria-hidden="true"></i> Top 100 </p><p class="new-listing__categories__category"> Full-Time </p><p class="new-listing__categories__category"> Anywhere in the World </p></div></div></a> """
                    # Get job URL
                    link_elem = job.get('a')  
                    job_url = urljoin('https://weworkremotely.com', link_elem['href']) if link_elem else '#'  # Fallback URL
                    
                    self.data.append({
                        'Job Title': title,
                        'Job Source': 'We Work Remotely',
                        'Category': self.get_category(title, ""),
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Job URL': job_url
                    })
                    print(f"Added job: {title}")
                except Exception as e:
                    print(f"Error processing We Work Remotely job: {str(e)}")
                    continue
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping We Work Remotely: {str(e)}")
            if driver:
                driver.quit()


    def scrape_fiverr(self):
        driver = None
        """Scrape job listings from Fiverr"""
        try:
            driver = self.setup_driver()
            driver.get(self.sites['fiverr'])
            time.sleep(5)
            
            # Wait for job elements to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.gig-card'))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('div', class_='gig-card')
            
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('h3', class_='gig-title')
                    description_elem = job.find('div', class_='gig-description')
                    
                    if title_elem and description_elem:
                        # Get job URL
                        job_url = None
                        if title_elem.find('a'):
                            job_url = self.sites['fiverr'] + title_elem.find('a')['href']
                        else:
                            job_url = "Not specified"
                        
                        title = self.clean_text(title_elem.text)
                        description = self.clean_text(description_elem.text)
                        
                        self.data.append({
                            'Job Title': title,
                            'Job Description': description,
                            'Job Source': 'Fiverr',
                            'Category': self.get_category(title, description),
                            'Job URL': job_url,
                            'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error processing Fiverr job: {e}")
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Fiverr: {e}")
    
    def scrape_wayup(self):
        driver = None
        """Scrape job listings from Wayup"""
        try:
            driver = self.setup_driver()
            driver.get(self.sites['wayup'])
            time.sleep(5)
            
            # Wait for job elements to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.gig-card'))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = soup.find_all('div', class_='gig-card')
            
            for job in jobs[0:31]:
                try:
                    title_elem = job.find('h3', class_='gig-title')
                    description_elem = job.find('div', class_='gig-description')
                    
                    if title_elem and description_elem:
                        # Get job URL
                        job_url = None
                        if title_elem.find('a'):
                            job_url = self.sites['wayup'] + title_elem.find('a')['href']
                        else:
                            job_url = "Not specified"
                        
                        title = self.clean_text(title_elem.text)
                        description = self.clean_text(description_elem.text)
                        
                        self.data.append({
                            'Job Title': title,
                            'Job Description': description,
                            'Job Source': 'Wayup',
                            'Category': self.get_category(title, description),
                            'Job URL': job_url,
                            'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error processing Wayup job: {e}")
            
            driver.quit()
        except Exception as e:
            print(f"Error scraping Wayup: {e}")

    def scrape_internships(self):
        driver = None
        """Scrape from internship-specific job boards"""
        print("Scraping internship-specific job boards...")
        try:
            # Internships.com
            try:
                response = requests.get(self.sites['internships'])
                soup = BeautifulSoup(response.text, 'html.parser')
                internships = soup.find_all('div', class_='internship')
                for internship in internships[0:31]:
                    try:
                        title = self.clean_text(internship.find('h3').text if internship.find('h3') else '')
                        company = self.clean_text(internship.find('h4').text if internship.find('h4') else '')
                        
                        # Get detailed description by following the job link
                        job_url = urljoin('https://www.internships.com', internship.find('a')['href'] if internship.find('a') else '#')
                        if job_url != '#':
                            try:
                                detail_response = requests.get(job_url)
                                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                description = self.clean_text(detail_soup.find('div', class_='description').text if detail_soup.find('div', class_='description') else '')
                                
                                # Get additional details
                                details = detail_soup.find_all('div', class_='detail')
                                location = ''
                                duration = ''
                                pay = ''
                                for detail in details:
                                    if 'location' in detail.text.lower():
                                        location = self.clean_text(detail.text)
                                    elif 'duration' in detail.text.lower():
                                        duration = self.clean_text(detail.text)
                                    elif 'pay' in detail.text.lower():
                                        pay = self.clean_text(detail.text)
                            except:
                                description = self.clean_text(internship.find('div', class_='description').text if internship.find('div', class_='description') else '')
                                location = duration = pay = 'Not specified'
                        else:
                            description = self.clean_text(internship.find('div', class_='description').text if internship.find('div', class_='description') else '')
                            location = duration = pay = 'Not specified'
                        
                        if title and description:  # Only add if we have both title and description
                            category = self.get_category(title, description)
                            self.internships.append({
                                'Job Title': title,
                                'Job Description': description,
                                'Job Source': 'Internships.com',
                                'Category': category,
                                'Location': location,
                                'Duration': duration,
                                'Pay': pay,
                                'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'Job URL': job_url
                            })
                    except Exception as e:
                        print(f"Error processing Internships.com job: {str(e)}")
                        continue
            except Exception as e:
                print(f"Error scraping Internships.com: {str(e)}")

            # Internshala
            try:
                response = requests.get(self.sites['internshala'])
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if the page loaded successfully
                if soup.find('div', class_='no_internships_found'):
                    print("No internships found on Internshala")
                
                # Try different class names for job listings
                internships = soup.find_all('div', class_='internship_meta')
                if not internships:
                    internships = soup.find_all('div', class_='internship')
                if not internships:
                    internships = soup.find_all('div', class_='internship_detail')
                
                for internship in internships[0:31]:
                    try:
                        # Try different selectors for title
                        title_elem = internship.find('div', class_='heading_4_5')
                        if not title_elem:
                            title_elem = internship.find('h3')
                        if not title_elem:
                            title_elem = internship.find('h2')
                        title = self.clean_text(title_elem.text if title_elem else '')
                        
                        # Try different selectors for company
                        company_elem = internship.find('div', class_='company_name')
                        if not company_elem:
                            company_elem = internship.find('h4')
                        company = self.clean_text(company_elem.text if company_elem else '')
                        
                        # Get detailed description by following the job link
                        link_elem = internship.find('a', href=True)
                        job_url = urljoin('https://internshala.com', link_elem['href']) if link_elem else '#'  # Fallback URL
                        
                        if job_url != '#':
                            try:
                                detail_response = requests.get(job_url)
                                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                description = self.clean_text(detail_soup.find('div', class_='internship_details').text if detail_soup.find('div', class_='internship_details') else '')
                                
                                # Get additional details
                                details = detail_soup.find_all('div', class_='detail')
                                location = ''
                                duration = ''
                                pay = ''
                                for detail in details:
                                    if 'location' in detail.text.lower():
                                        location = self.clean_text(detail.text)
                                    elif 'duration' in detail.text.lower():
                                        duration = self.clean_text(detail.text)
                                    elif 'pay' in detail.text.lower():
                                        pay = self.clean_text(detail.text)
                            except:
                                description = self.clean_text(internship.find('div', class_='internship_details').text if internship.find('div', class_='internship_details') else '')
                                location = duration = pay = 'Not specified'
                        else:
                            description = self.clean_text(internship.find('div', class_='internship_details').text if internship.find('div', class_='internship_details') else '')
                            location = duration = pay = 'Not specified'
                        
                        # Only add if we have both title and description
                        if title and description:
                            category = self.get_category(title, description)
                            self.internships.append({
                                'Job Title': title,
                                'Job Description': description,
                                'Job Source': 'Internshala',
                                'Category': category,
                                'Location': location,
                                'Duration': duration,
                                'Pay': pay,
                                'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'Job URL': job_url
                            })
                        else:
                            print(f"Skipping Internshala job - Missing title or description")
                            
                    except Exception as e:
                        print(f"Error processing Internshala job: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error scraping Internshala: {str(e)}")

            #remoteok_internships
            """Scrape internship listings from Remote OK"""
            print("Scraping Remote OK internships...")
            driver = None
            try:
                driver = self.setup_driver()
                print(f"Visiting URL: {self.sites['remoteok_internships']}")
                driver.get(self.sites['remoteok_internships'])
                time.sleep(5)
        
                # Wait for internship elements to be present
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.preventLink'))
                    )
                    print("Found internship elements")
                except Exception as e:
                    print(f"Error waiting for internship elements: {str(e)}")
                    print("Page source:")
                    print(driver.page_source[:1000])  # Print first 1000 chars of page source
            
                soup = BeautifulSoup(driver.page_source, 'html.parser')
        
                # Check if the page loaded successfully
                if soup.find('div', class_='no_internships_found'):
                    print("No internships found on RemoteOK")
                else:
                    # Find all internship listings - FIXED: removed extra dot
                    internships = soup.find_all('a', class_='preventLink')
                    print(f"Found {len(internships)} internship elements")
            
                for internship in internships[0:31]:
                    try:
                        title_elem = internship.find('h2')
                        if title_elem:
                            print(f"Found internship title: {title_elem.text}")
                        else:
                            print("No title element found")
                            continue
                        
                        title = self.clean_text(title_elem.text)
                    
                        # Get company info (optional)
                        company_elem = internship.find('span')
                        company = self.clean_text(company_elem.text) if company_elem else "N/A"
                    
                        # Get internship URL
                        internship_url = None
                        if internship.get('href'):
                            # Clean the URL
                            relative_url = internship['href']
                            if relative_url:
                                # Handle external URLs
                                if relative_url.startswith('http') or relative_url.startswith('https'):
                                    internship_url = relative_url
                                else:
                                    # Handle internal URLs
                                    internship_url = urljoin('https://remoteok.com', relative_url)
                                # Clean URL parameters
                                if '?' in internship_url:
                                    internship_url = internship_url.split('?')[0]
                                # Remove trailing slash if present
                                if internship_url.endswith('/'):
                                    internship_url = internship_url.rstrip('/')
                        else:
                            internship_url = '#'  # Fallback URL
                    
                        self.internships.append({
                        'Job Title': title,
                        'Job Source': 'Remote OK Internships',
                        'Category': self.get_category(title, ""),
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Job URL': internship_url
                        })
                        print(f"Added internship: {title}")
                    except Exception as e:
                        print(f"Error processing Remote OK internship: {str(e)}")
                        continue
                    
                    driver.quit()
            except Exception as e:
                print(f"Error scraping Remote OK internships: {str(e)}")
                if driver:
                    driver.quit()

            """ try:
                response = requests.get(self.sites['letsintern'])
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if the page loaded successfully
                if soup.find('div', class_='no_internships_found'):
                    print("No internships found on LetsIntern")
                
                # Try different class names for job listings
                internships = soup.find_all('div', class_='internship_meta')
                if not internships:
                    internships = soup.find_all('div', class_='internship')
                if not internships:
                    internships = soup.find_all('div', class_='internship_detail')
                
                for internship in internships:
                    try:
                        # Try different selectors for title
                        title_elem = internship.find('div', class_='heading_4_5')
                        if not title_elem:
                            title_elem = internship.find('h3')
                        if not title_elem:
                            title_elem = internship.find('h2')
                        title = self.clean_text(title_elem.text if title_elem else '')
                        
                        # Try different selectors for company
                        company_elem = internship.find('div', class_='company_name')
                        if not company_elem:
                            company_elem = internship.find('h4')
                        company = self.clean_text(company_elem.text if company_elem else '')
                        
                        # Get detailed description by following the job link
                        link_elem = internship.find('a', href=True)
                        job_url = urljoin('https://www.letsintern.com/internships/it-internships', link_elem['href']) if link_elem else '#'  # Fallback URL
                        
                        if job_url != '#':
                            try:
                                detail_response = requests.get(job_url)
                                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                description = self.clean_text(detail_soup.find('div', class_='internship_details').text if detail_soup.find('div', class_='internship_details') else '')
                                
                                # Get additional details
                                details = detail_soup.find_all('div', class_='detail')
                                location = ''
                                duration = ''
                                pay = ''
                                for detail in details:
                                    if 'location' in detail.text.lower():
                                        location = self.clean_text(detail.text)
                                    elif 'duration' in detail.text.lower():
                                        duration = self.clean_text(detail.text)
                                    elif 'pay' in detail.text.lower():
                                        pay = self.clean_text(detail.text)
                            except:
                                description = self.clean_text(internship.find('div', class_='internship_details').text if internship.find('div', class_='internship_details') else '')
                                location = duration = pay = 'Not specified'
                        else:
                            description = self.clean_text(internship.find('div', class_='internship_details').text if internship.find('div', class_='internship_details') else '')
                            location = duration = pay = 'Not specified'
                        
                        # Only add if we have both title and description
                        if title and description:
                            category = self.get_category(title, description)
                            self.internships.append({
                                'Job Title': title,
                                'Job Description': description,
                                'Job Source': 'Letsintern',
                                'Category': category,
                                'Location': location,
                                'Duration': duration,
                                'Pay': pay,
                                'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'Job URL': job_url
                            })
                        else:
                            print(f"Skipping Letsintern job - Missing title or description")
                            
                    except Exception as e:
                        print(f"Error processing Letsintern job: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error scraping Letsintern: {str(e)}") """

            #letsintern
            #continue changing code
            """Scrape internship listings from Lets Intern"""
            print("Scraping Lets Intern internships...")
            driver = None
            try:
                driver = self.setup_driver()
                print(f"Visiting URL: {self.sites['letsintern']}")
                driver.get(self.sites['letsintern'])
                time.sleep(5)
        
                # Wait for internship elements to be present
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.blank-link'))
                    )
                    print("Found internship elements")
                except Exception as e:
                    print(f"Error waiting for internship elements: {str(e)}")
                    print("Page source:")
                    print(driver.page_source[:1000])  # Print first 1000 chars of page source
            
                soup = BeautifulSoup(driver.page_source, 'html.parser')
        
                # Check if the page loaded successfully
                if soup.find('div', class_='no_internships_found'):
                    print("No internships found on LetsIntern")
                else:
                    # Find all internship listings - FIXED: removed extra dot
                    internships = soup.find_all('a', class_='blank-link')
                    print(f"Found {len(internships)} internship elements")
            
                for internship in internships[0:31]:
                    try:
                        title_elem = internship.find('h4', class_='truncate-normal')
                        if title_elem:
                            print(f"Found internship title: {title_elem.text}")
                        else:
                            print("No title element found")
                            continue
                        
                        title = self.clean_text(title_elem.text)
                    
                        # Get company info (optional)
                        company_elem = internship.find('div', class_='company-name')
                        company = self.clean_text(company_elem.text) if company_elem else "N/A"
                    
                        # Get internship URL
                        internship_url = None
                        if internship.get('href'):
                            # Clean the URL
                            relative_url = internship['href']
                            if relative_url:
                                # Handle external URLs
                                if relative_url.startswith('http') or relative_url.startswith('https'):
                                    internship_url = relative_url
                                else:
                                    # Handle internal URLs
                                    internship_url = urljoin('https://www.letsintern.com/internship/', relative_url)
                                # Clean URL parameters
                                if '?' in internship_url:
                                    internship_url = internship_url.split('?')[0]
                                # Remove trailing slash if present
                                if internship_url.endswith('/'):
                                    internship_url = internship_url.rstrip('/')
                        else:
                            internship_url = '#'  # Fallback URL
                    
                        self.internships.append({
                        'Job Title': title,
                        'Job Source': 'LetsIntern',
                        'Category': self.get_category(title, ""),
                        'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Job URL': internship_url
                        })
                        print(f"Added internship: {title}")
                    except Exception as e:
                        print(f"Error processing LetsIntern internship: {str(e)}")
                        continue
                    
                    driver.quit()
            except Exception as e:
                print(f"Error scraping LetsIntern internships: {str(e)}")
                if driver:
                    driver.quit()

            # Brightermonday
            try:
                response = requests.get(self.sites['brightermonday'])
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if the page loaded successfully
                if soup.find('div', class_='no_internships_found'):
                    print("No internships found on Brightermonday")
                
                # Try different class names for job listings
                internships = soup.find_all('div', class_='internship_meta')
                if not internships:
                    internships = soup.find_all('div', class_='internship')
                if not internships:
                    internships = soup.find_all('div', class_='internship_detail')
                
                for internship in internships[0:31]:
                    try:
                        # Try different selectors for title
                        title_elem = internship.find('div', class_='heading_4_5')
                        if not title_elem:
                            title_elem = internship.find('h3')
                        if not title_elem:
                            title_elem = internship.find('h2')
                        title = self.clean_text(title_elem.text if title_elem else '')
                        
                        # Try different selectors for company
                        company_elem = internship.find('div', class_='company_name')
                        if not company_elem:
                            company_elem = internship.find('h4')
                        company = self.clean_text(company_elem.text if company_elem else '')
                        
                        # Get detailed description by following the job link
                        link_elem = internship.find('a', href=True)
                        job_url = urljoin('https://www.brightermonday.co.ke/jobs/internship-graduate', link_elem['href']) if link_elem else '#'  # Fallback URL
                        
                        if job_url != '#':
                            try:
                                detail_response = requests.get(job_url)
                                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                description = self.clean_text(detail_soup.find('div', class_='internship_details').text if detail_soup.find('div', class_='internship_details') else '')
                                
                                # Get additional details
                                details = detail_soup.find_all('div', class_='detail')
                                location = ''
                                duration = ''
                                pay = ''
                                for detail in details:
                                    if 'location' in detail.text.lower():
                                        location = self.clean_text(detail.text)
                                    elif 'duration' in detail.text.lower():
                                        duration = self.clean_text(detail.text)
                                    elif 'pay' in detail.text.lower():
                                        pay = self.clean_text(detail.text)
                            except:
                                description = self.clean_text(internship.find('div', class_='internship_details').text if internship.find('div', class_='internship_details') else '')
                                location = duration = pay = 'Not specified'
                        else:
                            description = self.clean_text(internship.find('div', class_='internship_details').text if internship.find('div', class_='internship_details') else '')
                            location = duration = pay = 'Not specified'
                        
                        # Only add if we have both title and description
                        if title and description:
                            category = self.get_category(title, description)
                            self.internships.append({
                                'Job Title': title,
                                'Job Description': description,
                                'Job Source': 'Brightermonday',
                                'Category': category,
                                'Location': location,
                                'Duration': duration,
                                'Pay': pay,
                                'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'Job URL': job_url
                            })
                        else:
                            print(f"Skipping Brightermonday job - Missing title or description")
                            
                    except Exception as e:
                        print(f"Error processing Brightermonday job: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error scraping Brightermonday: {str(e)}")

            # G2i (Go2Intern)
            try:
                response = requests.get(self.sites['g2i'])
                soup = BeautifulSoup(response.text, 'html.parser')
                internships = soup.find_all('div', class_='job-card')
                for internship in internships[0:31]:
                    try:
                        title = self.clean_text(internship.find('h2').text if internship.find('h2') else '')
                        company = self.clean_text(internship.find('h3').text if internship.find('h3') else '')
                        description = self.clean_text(internship.find('div', class_='job-description').text if internship.find('div', class_='job-description') else '')
                        job_url = urljoin('https://g2i.co', internship.find('a')['href'] if internship.find('a') else '#')
                        
                        if title and description:  # Only add if we have both title and description
                            self.internships.append({
                                'Job Title': title,
                                'Job Description': description,
                                'Job Source': 'Go2Intern',
                                'Category': self.get_category(title, description),
                                'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'Job URL': job_url
                            })
                    except Exception as e:
                        print(f"Error processing Go2Intern job: {str(e)}")
                        continue
            except Exception as e:
                print(f"Error scraping Go2Intern: {str(e)}")

            # FrontendInterns
            try:
                response = requests.get(self.sites['frontendinterns'])
                soup = BeautifulSoup(response.text, 'html.parser')
                internships = soup.find_all('div', class_='job-listing')
                for internship in internships[0:31]:
                    try:
                        title = self.clean_text(internship.find('h2').text if internship.find('h2') else '')
                        company = self.clean_text(internship.find('h3').text if internship.find('h3') else '')
                        description = self.clean_text(internship.find('div', class_='job-description').text if internship.find('div', class_='job-description') else '')
                        job_url = urljoin('https://frontendinterns.com', internship.find('a')['href'] if internship.find('a') else '#')
                        
                        if title and description:  # Only add if we have both title and description
                            self.internships.append({
                                'Job Title': title,
                                'Job Description': description,
                                'Job Source': 'FrontendInterns',
                                'Category': self.get_category(title, description),
                                'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'Job URL': job_url
                            })
                    except Exception as e:
                        print(f"Error processing FrontendInterns job: {str(e)}")
                        continue
            except Exception as e:
                print(f"Error scraping FrontendInterns: {str(e)}")

        except Exception as e:
            print(f"Error scraping internship boards: {str(e)}")
    def run(self):
        """Run the scraper"""
        print("Starting job scraping...")
        try:
            # Scrape jobs only from major platforms
            self.scrape_indeed(is_internship=False)
            self.scrape_linkedin(is_internship=False)
            self.scrape_glassdoor(is_internship=False)
            
            # Scrape from internship-specific job boards
            self.scrape_internships()
            
            # Scrape from other sources
            #self.fetch_jobs()
            self.scrape_upwork()
            self.scrape_upwork_intern()
            self.scrape_freelancer()
            self.scrape_jobpresso()
            self.scrape_fiverr()
            self.scrape_pythonjobs()
            self.scrape_remoteok()
            self.scrape_g21()
            self.scrape_remotive()
            self.scrape_weworkremotely()
            self.scrape_wayup()

            
            # Save to Excel
            if self.data:
                df = pd.DataFrame(self.data)
                df.to_excel('job_listings.xlsx', index=False)
                print(f"Found {len(self.data)} jobs")
                print("Data saved to job_listings.xlsx")
            else:
                print("No data found")

            if self.internships:
                df = pd.DataFrame(self.internships)
                df.to_excel('internships.xlsx', index=False)
                print(f"Found {len(self.internships)} internships")
                print("Internship data saved to internships.xlsx")
            else:
                print("No internship data found")
            
            print("Job scraping completed!")
        except Exception as e:
            print(f"Error in scraper run: {str(e)}")

        
if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
