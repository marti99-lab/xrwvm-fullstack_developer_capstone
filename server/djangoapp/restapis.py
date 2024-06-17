import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', default="http://localhost:5050/")

def get_request(endpoint, **kwargs):
    try:
        response = requests.get(backend_url + endpoint, params=kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error during GET request to {endpoint}: {e}")
        return None

def analyze_review_sentiments(text):
    request_url = f"{sentiment_analyzer_url}analyze/{text}"
    try:
        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error during sentiment analysis request: {e}")
        return None

def post_review(data_dict):
    try:
        response = requests.post(backend_url + "reviews", json=data_dict)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error during POST request: {e}")
        return None