import boto3
from botocore.client import Config

# **MUST REPLACE 'storage.example.com' WITH YOUR ACTUAL DOMAIN**
MINIO_ENDPOINT = 'https://storage.example.com'
ACCESS_KEY = 'minioadmin'
SECRET_KEY = 'VeryStrongPassword123!'
BUCKET_NAME = 'red-cloud-bucket'
FILE_TO_UPLOAD = 'test_file.txt'

# 1. Create a dummy file for upload
with open(FILE_TO_UPLOAD, 'w') as f:
    f.write("This is a test file for the 'ضبابة الحمراء' (Red Cloud) storage.")

# 2. Initialize the S3 client
s3 = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1' # MinIO ignores this but boto3 requires it
)

try:
    # 3. Create the bucket
    print(f"Creating bucket: {BUCKET_NAME}")
    s3.create_bucket(Bucket=BUCKET_NAME)
    print("Bucket created successfully.")

    # 4. Upload the file
    print(f"Uploading file: {FILE_TO_UPLOAD}")
    s3.upload_file(FILE_TO_UPLOAD, BUCKET_NAME, FILE_TO_UPLOAD)
    print("File uploaded successfully.")

    # 5. List objects in the bucket
    print(f"Listing objects in bucket: {BUCKET_NAME}")
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    for obj in response.get('Contents', []):
        print(f"- {obj['Key']} ({obj['Size']} bytes)")

    # 6. Download the file
    download_path = f"downloaded_{FILE_TO_UPLOAD}"
    print(f"Downloading file to: {download_path}")
    s3.download_file(BUCKET_NAME, FILE_TO_UPLOAD, download_path)
    print("File downloaded successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
    print("\n**NOTE:** This script requires the MinIO server to be running and accessible via the specified MINIO_ENDPOINT.")
    
finally:
    # Clean up the local test file
    import os
    if os.path.exists(FILE_TO_UPLOAD):
        os.remove(FILE_TO_UPLOAD)
    if os.path.exists(download_path):
        os.remove(download_path)
