import os
import boto3
from pathlib import Path

SPACES_REGION = os.getenv("SPACES_REGION")
SPACES_ENDPOINT_URL = os.getenv("SPACES_ENDPOINT_URL")
SPACES_ACCESS_KEY = os.getenv("SPACES_ACCESS_KEY")
SPACES_SECRET_KEY = os.getenv("SPACES_SECRET_KEY")
SPACES_BUCKET_NAME = os.getenv("SPACES_BUCKET_NAME")

def get_spaces_client():
    return boto3.client(
        's3',
        region_name=SPACES_REGION,
        endpoint_url=SPACES_ENDPOINT_URL,
        aws_access_key_id=SPACES_ACCESS_KEY,
        aws_secret_access_key=SPACES_SECRET_KEY
    )

def list_folders(bucket_name, prefix):
    client = get_spaces_client()
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(
        Bucket=bucket_name,
        Prefix=prefix,
        Delimiter='/'   # This makes it return "folders"
    )

    folders = []
    for page in page_iterator:
        if 'CommonPrefixes' in page:
            for cp in page['CommonPrefixes']:
                folders.append(cp['Prefix'])
    return folders

def download_objects(bucket_name, prefix, local_base):
    client = get_spaces_client()
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    has_files = False
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                relative_path = os.path.relpath(key, prefix)
                local_path = os.path.join(local_base, prefix, relative_path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                print(f"⬇️ Downloading {key} -> {local_path}")
                client.download_file(bucket_name, key, local_path)
                has_files = True
    if not has_files:
        print(f"⚠️ No files under {prefix}!")

if __name__ == "__main__":
    LOCAL_BASE = "./downloaded_spaces"

    print("🚀 Connecting to Spaces...")

    # List folders under ml_models
    model_categories = list_folders(SPACES_BUCKET_NAME, "ml_models/")
    print(f"📂 Found model categories: {model_categories}")

    for category_prefix in model_categories:
        download_objects(SPACES_BUCKET_NAME, category_prefix, LOCAL_BASE)

    # List folders under data/
    data_categories = list_folders(SPACES_BUCKET_NAME, "data/")
    print(f"📂 Found data categories: {data_categories}")

    for data_prefix in data_categories:
        download_objects(SPACES_BUCKET_NAME, data_prefix, LOCAL_BASE)

    print("\n✅ DONE! All files downloaded.")
