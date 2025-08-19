import os
import re
import time

import requests
from azure.storage.blob import BlobClient
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")

load_dotenv(env_path)
WILEY_TDM_TOKEN = os.getenv("TDM_API_TOKEN")  # your Wiley token
AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")  # storage conn string
CONTAINER = "articles"  # your container
TDM_DELAY_SEC = 10  # Wiley limit (~1 req / 10s)
load_dotenv()


def doi_to_blob_name(doi: str) -> str:
    # filesystem-safe name, e.g. 10.1002/advs.202508912 -> 10.1002_advs.202508912.pdf
    return re.sub(r"[^A-Za-z0-9._-]+", "_", doi) + ".pdf"


def save_wiley_pdf_to_blob(doi: str, container: str = CONTAINER):
    # Wiley TDM endpoint for a DOI
    url = f"https://api.wiley.com/onlinelibrary/tdm/v1/articles/{doi}"
    headers = {"Wiley-TDM-Client-Token": WILEY_TDM_TOKEN, "Accept": "application/pdf"}

    # Create a BlobClient pointing to the target blob
    blob_name = doi_to_blob_name(doi)
    blob_client = BlobClient.from_connection_string(
        conn_str=AZURE_CONN_STR,
        container_name=container,
        blob_name=blob_name,
    )

    # Stream download from Wiley and stream-upload to Azure (no disk)
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        r.raise_for_status()
        blob_client.upload_blob(r.raw, overwrite=True, content_type="application/pdf")

    print(f"✅ Uploaded {doi} -> {blob_client.url}")
    time.sleep(TDM_DELAY_SEC)  # be nice to Wiley’s rate limits


# Example:
save_wiley_pdf_to_blob("10.1002/smll.202505866")
