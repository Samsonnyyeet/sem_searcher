import json
import requests
import threading
import requests
from bs4 import BeautifulSoup
import pandas as pd

API_KEY = "AIzaSyCuJPcMBd_jv5jTdFFW_nCHMujy8VxlJkk"
SEARCH_ENGINE_ID = "21f8592ba5377435a"

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

def get_dataset(query, results, rlinks):
    query = "how to securely read and process strings"
    results = make_request(build_payload(query, 1, 20))
    items = results['items']
    df = pd.json_normalize(items)

    # df = pd.read_excel(r"G:\Side_Quests\Code_of_Honor\search_result.xlsx")

    # Define a function to scrape a single link
    def scrape_link(url, result, rlink):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
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
