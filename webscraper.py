from bs4 import BeautifulSoup
import requests
import json

tweetArr =[]

url = "https://ethans_fake_twitter_site.surge.sh/"
response = requests.get(url, timeout = 5, verify=False)
content = BeautifulSoup(response.content, "html.parser")

for tweet in content.findAll('div', attrs={"class": "tweetcontainer"}):
    tweetObject = {
        "date": tweet.find('h5', attrs={"class": "dateTime"}).text.strip(),
        "likes": tweet.find('p', attrs={"class": "likes"}).text.strip(),
        "shares": tweet.find('p', attrs={"class": "shares"}).text.strip()
    }
    tweetArr.append(tweetObject)

with open('data.json', 'w') as outfile:
    json.dump(tweetArr, outfile, indent=4)