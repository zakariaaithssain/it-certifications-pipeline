# IT Certifications Pipeline

This project scrapes, cleans, ml enforces, and plots metadata of IT certifications from providers: AWS, Microsoft, and CompTIA.

## 📌 Features

- 🔍 Web scraping of certifications metadata.
- 🧹 Data cleaning, formatting, standardizing, concatenating and exporting.
- 📈 Data enhancement using ML models.
- 📊 Data analysis visualizations


## 📁 Project Structure

- `scraping/` - Scrapers and source data
- `data/` - Cleaned, raw, and processed datasets
- `cleaning/` -Cleaners 
- `analysis/` - EDA and visualizations
- `ml/` - machine learning related data enhancement
- `a Streamlit UI`

# How to use:
Please consider adapting different paths used in the project to your case.
Run the treamlit UI that will guide you throughout the pipeline steps. Orcrun each step independently from the run_step.py file (e.g. run_scraping.py to run scraping), as classes are built to be both compatible with the UI and runnable independently.

# Note:
Web scraping classes are HTML-structure sensitive, so any changing in the structure of the website could damage or totally break the scraper.
In this case, consider debugging the class to find and replace the tag(s) and/or attribute(s) that have been changed.

