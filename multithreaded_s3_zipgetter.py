
import os
import zipfile
from io import BytesIO
from tqdm import tqdm
import re
import boto3
import threading
from dotenv import load_dotenv

load_dotenv()

def clean_path(path):
    # Decoding URL-encoded characters
    path = re.sub(r'%2c', ',', path)
    # Removing or replacing other unwanted characters. Add more as needed.
    path = re.sub(r'[^a-zA-Z0-9_\-./]', '_', path)  # Replacing any unusual character with underscore
    return path

def unzip_file(zip_content, zip_file_key):
    # Create a subfolder based on the ZIP file name
    subfolder_name = os.path.join("crypts", os.path.splitext(os.path.basename(zip_file_key))[0])
    subfolder_name = clean_path(subfolder_name)
    os.makedirs(subfolder_name, exist_ok=True)

    # Extract the ZIP file's content into the subfolder
    with zipfile.ZipFile(BytesIO(zip_content)) as z:
        for file_info in z.infolist():
            file_path = os.path.join(subfolder_name, file_info.filename)
        
            # Check if the file already exists
            if not os.path.exists(file_path):
                file_data = z.read(file_info.filename)
                
                # Write the file data to the subfolder
                with open(file_path, 'wb') as f:
                    f.write(file_data)

# Load S3 configurations from environment variables
bucket_name = os.getenv("S3_BUCKET_NAME")
search_prefix = os.getenv("S3_SEARCH_PREFIX")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize the boto3 S3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

# List objects in the specified S3 bucket and prefix
objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=search_prefix)

# Filter out the .zip files from the list
zip_files = [obj['Key'] for obj in objects.get('Contents', []) if obj['Key'].endswith('.zip')]

if not zip_files:
    print("No ZIP files found in the specified S3 location.")
else:
    threads = []  # List to keep track of threads
    for zip_file_key in tqdm(zip_files):
        # Download the ZIP file from S3
        zip_obj = s3_client.get_object(Bucket=bucket_name, Key=zip_file_key)
        zip_content = zip_obj['Body'].read()
        
        # Create a new thread for unzipping and start it
        t = threading.Thread(target=unzip_file, args=(zip_content, zip_file_key))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
