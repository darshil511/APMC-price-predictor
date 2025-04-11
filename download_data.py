import os
import boto3
from botocore.exceptions import NoCredentialsError

# Configuration
SPACES_KEY = os.getenv("SPACES_ACCESS_KEY")      # Set these as environment variables
SPACES_SECRET = os.getenv("SPACES_SECRET_KEY")
SPACES_REGION = os.getenv("SPACES_REGION")
SPACES_ENDPOINT = os.getenv("SPACES_ENDPOINT_URL")
BUCKET_NAME = os.getenv("SPACES_BUCKET_NAME")
LOCAL_ROOT_DIR = os.getenv("BASE_DIRECTORY")

# Connect to Spaces
session = boto3.session.Session()
client = session.client(
    's3',
    region_name=SPACES_REGION,
    endpoint_url=SPACES_ENDPOINT,
    aws_access_key_id=SPACES_KEY,
    aws_secret_access_key=SPACES_SECRET
)

def download_all_objects():
    try:
        paginator = client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=BUCKET_NAME)

        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                local_path = os.path.join(LOCAL_ROOT_DIR, key)

                # Create local directories if needed
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # Download the file
                print(f"Downloading {key} to {local_path}")
                client.download_file(BUCKET_NAME, key, local_path)

        print("✅ All files downloaded successfully.")
    except NoCredentialsError:
        print("❌ Credentials not found. Set SPACES_ACCESS_KEY and SPACES_SECRET_KEY.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    download_all_objects()
