import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env file
WILEY_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(WILEY_PATH)
WILEY_TOKEN = os.getenv("TDM_API_TOKEN")

try:
    WILEY_TDM_TOKEN = load_dotenv(WILEY_PATH)
except KeyError:
    print("Token not found. Please set 'WILEY_TDM_TOKEN' in your .env file.")

doi = "10.1002/adfm.202412406"

# DOI of article to download


def fetch_wiley_article(doi: str):
    """
    Fetch a Wiley article PDF using the Wiley TDM API.
    """
    url = f"https://api.wiley.com/onlinelibrary/tdm/v1/articles/{doi}"
    headers = {"Wiley-TDM-Client-Token": WILEY_TOKEN}
    response = requests.get(url, headers=headers)

    # Download PDF if status code indicates success
    if response.status_code == 200:
        filename = f"{doi.replace('/', '_')}.pdf"
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"{filename} downloaded successfully")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
