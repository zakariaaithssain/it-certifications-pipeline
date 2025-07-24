# IT Certifications Pipeline (CompTIA changed the layout, the scraper is  a lil broken. (but data is still available))
 
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
- `imputing/` - machine learning based data imputers
- `a Streamlit UI`

# How to use:
Please consider adapting different paths used in the project to your case.
Run the interface.py file from the project root for the UI, or run each step independently from the run_step.py file (e.g. run_scraping.py to run scraping), as classes are built to be both runnable independently and compatible with the UI.

# Note:
Web scraping classes are HTML-structure sensitive, and the other classes depend on the scraping one, so any changes in the structure of a website could damage or totally break the scraper, hence the rest of the pipeline.
In this case, consider debugging the class to find and replace the tag(s) and/or attribute(s) that have been changed, and also the other classes if needed. Also consider opening an issue in the GitHub repository to notify me of the change, so that it can be fixed in the next release.

