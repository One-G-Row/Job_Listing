# Freelance Job Listings Scraper

This tool scrapes job listings from popular freelance websites and saves them to an Excel spreadsheet. It also provides a web-based UI to view the scraped data.

## Features

- Scrapes job listings from multiple freelance sites (Upwork, Freelancer)
- Extracts job title, description, price, and posting date
- Saves data to an Excel spreadsheet
- Web-based UI to view job listings
- Headless browser operation for better performance

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the scraper to collect job listings:
   ```bash
   python job_scraper.py
   ```

2. Start the web UI:
   ```bash
   python app.py
   ```

3. Open your web browser and go to:
   http://localhost:5000

The web interface will show:
- Total number of jobs found
- Sources of the job listings
- A searchable and sortable table of all job listings

## Output Format

The Excel file will contain the following columns:
- Site: The freelance website where the job was posted
- Title: Job title
- Description: Job description
- Price: Proposed price/rate
- Date: When the job was scraped
