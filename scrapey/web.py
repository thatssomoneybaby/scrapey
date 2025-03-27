import requests
from bs4 import BeautifulSoup

def extract_web_text(url):
    """
    Extract and return the text content from a web page using requests and BeautifulSoup.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching URL: {response.status_code}")
    soup = BeautifulSoup(response.text, "html.parser")
    # Get all text, separating by newlines
    return soup.get_text(separator="\n") 