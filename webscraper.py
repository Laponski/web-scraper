from bs4 import BeautifulSoup
import requests
import json
import os

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

# URL of the page you want to get the images from
url = 'https://www.liceosteamemilia.com/' 

# Esegui lo scraping delle immagini
image_urls = search_images(url)

# Create json dictionary
data = {"image_urls": image_urls}

# Save images in data.json
with open('data.json', 'w') as f:
    json.dump(data, f, indent=4)
    # Inform user that images have been saved 
    print("Image URLs have been saved to data.json")
