from scrapers import CompTIA, AWS, Microsoft

sites = [CompTIA(), AWS(), Microsoft()]
for site in sites:
    print(f'Scraping {site.name}...')
    site.scraper()
    site.save_to_json(fr'..\data\raw\raw_{site.name}_certifications.json')

else: print('Scraping Finished Successfully')