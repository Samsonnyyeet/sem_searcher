import json
import threading
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request
import requests

API_KEY = ""
SEARCH_ENGINE_ID = ""

def build_payload(query, start=1, num=10, **params):
    payload = {
        'key': API_KEY,
        'q' : query,
        'cx' : SEARCH_ENGINE_ID,
        'start' : start,
        'num' : num,
    }
    payload.update(params)
    return payload

def make_request(payload):
    url = "https://www.googleapis.com/customsearch/v1" 
    response = requests.get(url, params = payload)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise Exception(f"Google Request Failed : {response.status_code}")

def get_dataset(query, num_of_results, results, rlinks):
    # query = "how to securely read and process strings"
    rem = num_of_results % 10
    if rem > 0 :
        pages = (num_of_results // 10) + 1
    else:
        pages = (num_of_results // 10)
    
    items = list()
    for i in range(pages):
        if pages == (i+1) and rem > 0 :
            payload = build_payload(query, start = (i+1)*10, num = rem)
        else:
            payload = build_payload(query, start = (i+1)*10)
        response = make_request(payload)
        items.extend(response["items"])
    # results = make_request(build_payload(query, 1, 20))
    # items = results['items']
    df = pd.json_normalize(items)
    df.to_excel(f"{query}_{0}.xlsx")
    # df = pd.read_excel(r"G:\Side_Quests\Code_of_Honor\search_result.xlsx")

    # Define a function to scrape a single link
    def scrape_link(url, result, rlink):
        try:
            try:
                req = urllib.request.Request(url,data=None, 
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
                f11 = urllib.request.urlopen(req)
                html=f11.read().decode('utf-8')
            except:
                return(' ')
            # response = requests.get(url)
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all('p')
            paragraphs.pop()
            paragraphs.pop()
            for paragraph in paragraphs:
                temp = paragraph.text
                if len(temp) > 10:
                    result.append(temp)
                    rlink.append(url)
        except Exception as e:
            print(e)

    urls = df['link']
    # rlinks=list()
    # results = list()

    threads = []

    # Create threads for each URL and start them
    for url in urls:
        thread = threading.Thread(target=scrape_link, args=(url, results, rlinks))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
