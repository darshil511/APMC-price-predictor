import boto3
import os

SPACES_REGION = "us-east-1"
SPACES_ENDPOINT_URL = "https://apmc-ml-models.sfo3.digitaloceanspaces.com"
SPACES_ACCESS_KEY = "DO801T4Y2XGLAGTN2TDP"
SPACES_SECRET_KEY = "PtSEZ4g6Sdo6JY1AFQffrXAueiXghu+XMvxnjYMu0gM"
SPACES_BUCKET_NAME = "apmc-ml-models"

print(SPACES_REGION)
print(SPACES_ENDPOINT_URL)
print(SPACES_ACCESS_KEY)
print(SPACES_SECRET_KEY)
print(SPACES_BUCKET_NAME)

def get_spaces_client():
    return boto3.client(
        's3',
        region_name=SPACES_REGION,
        endpoint_url=SPACES_ENDPOINT_URL,
        aws_access_key_id=SPACES_ACCESS_KEY,
        aws_secret_access_key=SPACES_SECRET_KEY
    )

def list_categories(bucket_name, prefix):
    client = get_spaces_client()

    response = client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix,          # e.g., "ml_models/"
        Delimiter='/'           # <-- the magic part
    )

    categories = []
    if 'CommonPrefixes' in response:
        for cp in response['CommonPrefixes']:
            # Remove prefix base to get only folder name
            folder_name = cp['Prefix'][len(prefix):].rstrip('/')
            categories.append(folder_name)

    return categories

def test():
    client = get_spaces_client()
    print(client.list_buckets())
    print(client.list_objects(Bucket="apmc-ml-models"))

if __name__ == "__main__":
    print("🧾 Listing categories in 'ml_models/' ...")

    # categories = list_categories(SPACES_BUCKET_NAME, "ml_models/")
    # for cat in categories:
    #     print(f"📁 {cat}")
    
    test()
