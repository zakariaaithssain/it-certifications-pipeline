import requests as req
response = req.get('https://www.technopark.ma/sitemap_index.xml')
if response.status_code == 200:
    sitemap = response.text
    print(sitemap)
else: 
    print(f"Error: {response.status_code}")
    print("Failed to retrieve the sitemap.")