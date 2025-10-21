import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client("articles")
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING
)


def list_blob():
    container_name = "articles"

    # get connection string from env
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

    # connect to blob service
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # get container client
    container_client = blob_service_client.get_container_client(container_name)
    list_blobs = []
    # list blobs
    for blob in container_client.list_blobs():
        list_blobs.append(blob.name)
    return list_blobs


# Call the function
# list_blob()


def delete_blob():
    for blob in container_client.list_blobs():
        blob_name = blob.name
        container_client.delete_blob(blob_name)


# delete_blob()


def upload_blob():
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(
        "articles"
    )  # Use the correct container name

    # Path to the pdfs folder (one level up from Azure)
    pdfs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pdfs"))
    if not os.path.isdir(pdfs_dir):
        print(f"PDFs folder not found: {pdfs_dir}")
        return

    # Get list of existing blobs in the container
    existing_blobs = set(blob.name for blob in container_client.list_blobs())

    # Upload all PDF files in the pdfs folder if not already in blob storage
    for filename in os.listdir(pdfs_dir):
        if filename.lower().endswith(".pdf"):
            if filename in existing_blobs:
                print(f"Already exists in blob storage: {filename}")
                continue
            full_file_path = os.path.join(pdfs_dir, filename)
            if os.path.isfile(full_file_path):
                with open(full_file_path, "rb") as fl:
                    container_client.upload_blob(
                        name=filename, data=fl, overwrite=False
                    )
                    print(f"Uploaded: {filename}")
            else:
                print(f"File not found: {filename}")


# upload_blob()


def generate_sas_url(blob_name):
    # Use your connection string
    container_name = "articles"

    # Connect to blob service
    bsc = BlobServiceClient.from_connection_string(conn_str)

    # Generate SAS token
    sas_token = generate_blob_sas(
        account_name=bsc.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=bsc.credential.account_key,  # pulled from your connection string
        permission=BlobSasPermissions(read=True),  # read-only access
        expiry=datetime.utcnow() + timedelta(hours=1),  # valid for 1 hour
    )

    # Build full URL
    account_url = f"https://{bsc.account_name}.blob.core.windows.net"
    sas_url = f"{account_url}/{container_name}/{blob_name}?{sas_token}"

    return sas_url


# article = generate_sas_url()
