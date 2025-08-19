import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env file
WILEY_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(WILEY_PATH)
WILEY_TOKEN = os.getenv("TDM_API_TOKEN")

try:
    WILEY_TDM_TOKEN = load_dotenv(WILEY_PATH)
except KeyError:
    print("Token not found. Please set 'WILEY_TDM_TOKEN' in your .env file.")

doi = "doi/10.1002/smll.202505866"
# DOI of article to download
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

"""TDM Client Example 1 - Single PDF Download

This example demonstrates downloading a single Open Access Article PDF.
Files are saved to the 'downloads' directory relative to the current working directory.

Requirements:
    - Virtual environment activated
    - TDM_API_TOKEN environment variable set
    - wiley-tdm package installed

Output:
    - downloads/<doi>.pdf file(s)
"""


# # Setup logging
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
# )

# # Initialize client (uses TDM_API_TOKEN from environment)
# tdm = TDMClient()  # Will use TDM_API_TOKEN from environment

# # Download a single Article PDF
# tdm.download_pdf("10.1002/adem.202501118")
