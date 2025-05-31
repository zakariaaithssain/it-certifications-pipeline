from scraping.scrapers import CompTIA, AWS, Microsoft
def run_scraping(state = None, progress = None):  #those are streamlit interface related arguments
    try:
        sites = [CompTIA(), AWS(), Microsoft()]
        for i, site in enumerate(sites):
            if state is not None: state.text(f"Scraping {site.name}...")
            print(f'Scraping {site.name}...')
            site.scraper()
            site.save_to_json(fr'C:\Users\zakar\OneDrive\Bureau\PFA\raw_{site.name}_certifications.json')
            if progress is not None: progress.progress((i+1)/3)
        else:
            print('Scraping Finished Successfully')
            if state is not None: return True
    except Exception as e:
        print(f'Error while scraping: {e}')
        if state is not None:  return False