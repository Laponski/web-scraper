from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
import requests
import json
import os
from urllib.parse import urljoin, urlparse
import sys

app = Flask(__name__)

def progress_bar(progress, total): # Define a function to print a progres bar in the terminal
    if total == 0:
        percent = 0
    else:
        percent = 100 * (progress / float(total))
    
    percent = min(percent, 100)  # Ensures that the maximum percentage is 100
    bar_length = int(percent)
    bar = '█' * bar_length + '-' * (100 - bar_length) 
    sys.stdout.write('\r')
    sys.stdout.write(f"|{bar}| {percent:.2f}%")
    sys.stdout.flush()

# Define set fo variablet to take track of visited urls and all the images found
visited_urls = set()
all_image_urls = set()

# Define a function to search all the images in a url
def search_images(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        new_image_urls = set()

        # If the content is HTML searches objects with tag <img>
        if response.headers.get('Content-Type', '').split(';')[0] == 'text/html':
            soup = BeautifulSoup(response.content, 'html.parser')
            images = soup.find_all('img')
            for img in images:
                src = img.get('src')
                if src:
                    if src.startswith('http'):
                        new_image_urls.add(src)
                    else:
                        new_image_urls.add(urljoin(url, src))

        # If content type is not HTML and there are no <img> tags left, it searches images directly in the answer
        if not new_image_urls:
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            if content_type.startswith('image/'):
                new_image_urls.add(url)

        # Add the new images found to a global set of them
        all_image_urls.update(new_image_urls)

        return list(new_image_urls)

    except requests.exceptions.RequestException as e:
        # print(f"Error requesting {url}: {e}")
        return []
    except Exception as e:
        # print(f"Error parsing content from {url}: {e}")
        return []

# Define a function to search all the possible accesstible urls from a single one
def find_urls(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        if response.headers.get('Content-Type', '').split(';')[0] != 'text/html':
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        found_urls = set()

        # Find all <a> tags with attribute 'href'
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            # Changes URL from relative to absolute
            absolute_url = urljoin(url, href)
            # Ensures to not exit the initial domain
            if urlparse(absolute_url).netloc == urlparse(url).netloc:
                found_urls.add(absolute_url)

        return list(found_urls)

    except requests.exceptions.RequestException as e:
        # print(f"Error during request at {url}: {e}")
        return []
    except Exception as e:
        # print(f"Error during HTML parsing of {url}: {e}")
        return []

# Define a recursive function to search all the images in all urls
def recursive_scrape(url, check_footer=True):
    global all_urls  # Declare global variable

    # If the url is already visited stop
    if url in visited_urls:
        return
    
    # Adds the found url to the list of all the found urls
    visited_urls.add(url)
    
    # Updates the progres bar
    progress_bar(len(visited_urls), len(all_urls))

    # Starts scraping images
    image_urls = search_images(url)
    progress_bar(len(visited_urls), len(all_urls))  # Regularly updates the progress bar
    all_image_urls.update(image_urls)  # Updates directly the set with all the image urls
    
    # Finds new urls
    all_urls = find_urls(url)
    
    # Starts the recursive part for every new url
    for new_url in all_urls:
        recursive_scrape(new_url, check_footer=False if url == start_url else True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        global visited_urls, all_image_urls, all_urls, start_url

        visited_urls = set()
        all_image_urls = set()
        all_urls = []

        start_url = request.form['url']
        
        initial_urls = find_urls(start_url)
        total_urls = len(initial_urls) + 1

        recursive_scrape(start_url)

        all_image_urls_list = list(all_image_urls)

        combined_data = {
            "image_urls": all_image_urls_list,
            "urls": list(visited_urls)
        }

        return render_template_string(html_template, data=combined_data)

    return render_template_string(html_template, data=None)

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Web Scraper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 900px;
            margin: 50px auto;
            background: #fff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #4CAF50;
            font-size: 60px;
        }
        .input-container {
            margin-bottom: 20px;
            text-align: center;
        }
        input[type="text"] {
            width: 70%;
            padding: 10px;
            margin-right: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .results {
            margin-top: 20px;
        }
        .results h2 {
            color: #4CAF50;
        }
        .results ul {
            list-style-type: none;
            padding: 0;
        }
        .results li {
            background: #f9f9f9;
            margin: 5px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .results li a {
            color: #333;
            text-decoration: none;
        }
        .results li a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web Scraper</h1>
        <div class="input-container">
            <form method="post">
                <input type="text" name="url" placeholder="Enter URL" required>
                <button type="submit">Scrape</button>
            </form>
        </div>
        {% if data %}
        <div class="results">
            <h2>Image URLs</h2>
            <ul>
                {% for img_url in data.image_urls %}
                <li><a href="{{ img_url }}" target="_blank">{{ img_url }}</a></li>
                {% endfor %}
            </ul>
            <h2>All URLs</h2>
            <ul>
                {% for url in data.urls %}
                <li><a href="{{ url }}" target="_blank">{{ url }}</a></li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)