from scraping.scrapers import CompTIA, AWS, Microsoft
def run_scraping(state, progress):  #those are st interface related arguments
    try:
        sites = [CompTIA(), AWS(), Microsoft()]
        for i, site in enumerate(sites):
            state.text(f"Scraping {site.name}...")
            print(f'Scraping {site.name}...')
            site.scraper()
            site.save_to_json(fr'C:\Users\zakar\OneDrive\Bureau\PFA\raw_{site.name}_certifications.json')
            progress.progress((i+1)/3)
        else:
            print('Scraping Finished Successfully')
            return True
    except: return False