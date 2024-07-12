from flask import Flask, request, render_template_string, session, redirect, url_for
from bs4 import BeautifulSoup
import requests
import json
import os
from urllib.parse import urljoin, urlparse
import sys
import uuid

app = Flask(__name__)
app.secret_key = 'il_tuo_segreto_super_segreto_e_univoco'

def progress_bar(progress, total):
    if total == 0:
        percent = 0
    else:
        percent = 100 * (progress / float(total))
    
    percent = min(percent, 100)
    bar_length = int(percent)
    bar = '█' * bar_length + '-' * (100 - bar_length)
    sys.stdout.write('\r')
    sys.stdout.write(f"|{bar}| {percent:.2f}%")
    sys.stdout.flush()

visited_urls = set()
all_image_urls = set()

def search_images(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        new_image_urls = set()

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

        if not new_image_urls:
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            if content_type.startswith('image/'):
                new_image_urls.add(url)

        all_image_urls.update(new_image_urls)

        return list(new_image_urls)

    except requests.exceptions.RequestException as e:
        return []
    except Exception as e:
        return []

def find_urls(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        if response.headers.get('Content-Type', '').split(';')[0] != 'text/html':
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        found_urls = set()

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            absolute_url = urljoin(url, href)
            if urlparse(absolute_url).netloc == urlparse(url).netloc:
                found_urls.add(absolute_url)

        return list(found_urls)

    except requests.exceptions.RequestException as e:
        return []
    except Exception as e:
        return []

def recursive_scrape(url, check_footer=True):
    global all_urls

    if url in visited_urls:
        return
    
    visited_urls.add(url)
    
    progress_bar(len(visited_urls), len(all_urls))

    image_urls = search_images(url)
    progress_bar(len(visited_urls), len(all_urls))
    all_image_urls.update(image_urls)
    
    all_urls = find_urls(url)
    
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

        if not os.path.exists('static'):
            os.makedirs('static')

        filename = f"data_{uuid.uuid4().hex}.json"
        filepath = os.path.join('static', filename)

        with open(filepath, 'w') as f:
            json.dump(combined_data, f, indent=4)
        
        print(f"Data saved to {filepath}")

        session['data_file'] = filename
        session['page'] = 0

        return redirect(url_for('index'))

    data_file = session.get('data_file')
    page = session.get('page', 0)

    if data_file:
        filepath = os.path.join('static', data_file)
        with open(filepath, 'r') as f:
            combined_data = json.load(f)
        start_idx = page * 50
        end_idx = start_idx + 50
        image_urls_page = combined_data['image_urls'][start_idx:end_idx]
    else:
        image_urls_page = []

    return render_template_string(html_template, image_urls=image_urls_page, page=page, total=(len(combined_data['image_urls']) // 50) if data_file else 0)

@app.route('/next')
def next_page():
    page = session.get('page', 0)
    session['page'] = page + 1
    return redirect(url_for('index'))

@app.route('/prev')
def prev_page():
    page = session.get('page', 0)
    if page > 0:
        session['page'] = page - 1
    return redirect(url_for('index'))

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
            text-align: center;
        }
        .results li img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
        .pagination {
            text-align: center;
            margin-top: 20px;
        }
        .pagination button {
            padding: 10px 15px;
            margin: 0 5px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .pagination button:hover {
            background-color: #45a049;
        }
        .pagination button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
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
        {% if image_urls %}
        <div class="results">
            <h2>Images</h2>
            <ul>
                {% for img_url in image_urls %}
                <li><a href="{{ img_url }}" target="_blank"><img src="{{ img_url }}" alt="Image"></a></li>
                {% endfor %}
            </ul>
        </div>
        <div class="pagination">
            <form action="{{ url_for('prev_page') }}" method="get" style="display: inline;">
                <button type="submit" {% if page == 0 %}disabled{% endif %}>Previous</button>
            </form>
            <form action="{{ url_for('next_page') }}" method="get" style="display: inline;">
                <button type="submit" {% if page >= total %}disabled{% endif %}>Next</button>
            </form>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
