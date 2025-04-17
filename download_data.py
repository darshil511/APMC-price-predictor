import boto3
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

SPACES_REGION = os.getenv("SPACES_REGION")
SPACES_ENDPOINT_URL = f"https://{SPACES_REGION}.digitaloceanspaces.com"
SPACES_ACCESS_KEY = os.getenv("SPACES_ACCESS_KEY")
SPACES_SECRET_KEY = os.getenv("SPACES_SECRET_KEY")
SPACES_BUCKET_NAME = os.getenv("SPACES_BUCKET_NAME")

# Set your local download base directory
LOCAL_DOWNLOAD_PATH = "./APMC-price-predictor"

def get_spaces_client():
    return boto3.client(
        's3',
        region_name=SPACES_REGION,
        endpoint_url=SPACES_ENDPOINT_URL,
        aws_access_key_id=SPACES_ACCESS_KEY,
        aws_secret_access_key=SPACES_SECRET_KEY
    )

def download_space_folder(bucket_name, prefix, download_dir):
    client = get_spaces_client()

    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    files_downloaded = 0

    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                if key.endswith('/'):
                    continue  # Skip "folders" (S3 is flat, folders are virtual)

                # Compute local path
                relative_path = key[len(prefix):].lstrip('/')
                local_path = os.path.join(download_dir, relative_path)

                # Ensure local directory exists
                Path(local_path).parent.mkdir(parents=True, exist_ok=True)

                print(f"⬇️ Downloading: {key} → {local_path}")
                client.download_file(bucket_name, key, local_path)
                files_downloaded += 1

    print(f"\n✅ Download completed! Total files downloaded: {files_downloaded}")

if __name__ == "__main__":
    target_prefix = "apmc-ml-models/data/"
    target_local_folder = os.path.join(LOCAL_DOWNLOAD_PATH, "data")
    download_space_folder(SPACES_BUCKET_NAME, target_prefix, target_local_folder)
    
    target_prefix = "apmc-ml-models/ml_models/"
    target_local_folder = os.path.join(LOCAL_DOWNLOAD_PATH, "ml_models")
    download_space_folder(SPACES_BUCKET_NAME, target_prefix, target_local_folder)
