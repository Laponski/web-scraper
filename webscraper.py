from bs4 import BeautifulSoup
import requests
import json
import os
from urllib.parse import urljoin

def search_images(url):
    try:
        # Execute a GET request for the URL provided
        response = requests.get(url)
        response.raise_for_status()  # Controls if request had success
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return []

    # Analyze html content of URL provided
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the images in the file
    images = soup.find_all('img')

    # List to store image URLs
    image_urls = []

    for img in images:
        src = img.get('src')  # Extract the value of the 'src' attribute of each <img> tag
        if src: # Check if 'src' is not None or an empty string
    
            if src.startswith('http'): # Check if 'src' is an absolute URL
                image_urls.append(src) # Add the absolute URL to the list
            else:
                image_urls.append(os.path.join(url, src))  # Converts URL into absolute and appends to the list

    return image_urls

def find_urls(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    found_urls = set()  # Use a set to avoid duplicates

    # Find all <a> tags with 'href' attribute
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        # Resolve relative URLs to absolute URLs
        absolute_url = urljoin(url, href)
        found_urls.add(absolute_url)

    return list(found_urls)

# URL of the page you want to get the images from
steam_url = 'https://www.liceosteamemilia.com/' 

# Esegui lo scraping delle immagini
image_urls = search_images(steam_url)
all_urls = find_urls(steam_url)
# Create json dictionary
data = {"image_urls": image_urls}
urls = {"urls": all_urls}


# Save images in data.json
with open('data.json', 'w') as f:
    json.dump(data, f, indent=4)
    json.dump(urls, f, indent=4)
    # Inform user that images have been saved 
    print("Image URLs have been saved to data.json")
    print(f"Found {len(all_urls)} total URLs on the site {steam_url}.")
    print("URLs have been saved to data.json.")