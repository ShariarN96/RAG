import os

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")

load_dotenv(env_path)

conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client("articles")


def list_blob():
    container_name = "articles"

    # get connection string from env
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

    # connect to blob service
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # get container client
    container_client = blob_service_client.get_container_client(container_name)

    # list blobs
    for blob in container_client.list_blobs():
        print(blob.name)


# Call the function
list_blob()


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


upload_blob()
