import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__)
env_path = Path(__file__).parent.parent.parent / ".env"

load_dotenv(env_path)


class AzureBlobStorage:
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "articles")
        self.service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        self.container_client = self.service_client.get_container_client(
            self.container_name
        )

    def upload_files(self):
        upload_blob(self.container_client)

    def download_blob(self, blob_name: str) -> bytes:
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.download_blob().readall()

    def list_blobs(self, prefix: str = ""):
        return [
            blob.name
            for blob in self.container_client.list_blobs(name_starts_with=prefix)
        ]

    def delete_blob(self, blob_name: str):
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.delete_blob()

    def blob_exists(self, blob_name: str) -> bool:
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.exists()


x = AzureBlobStorage()
x.upload_files()


x.list_blobs()


def upload_blob(container_client):
    pdfs_dir = CURRENT_DIR.parent.parent.parent / "pdfs"
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
