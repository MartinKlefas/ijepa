import os
import sys
import time
import shutil
from datetime import datetime
import argparse

import zipfile
from io import BytesIO
from tqdm import tqdm
import re
import boto3
from dotenv import load_dotenv

load_dotenv()

def clean_path(path):
    # Decoding URL-encoded characters
    path = re.sub(r'%2c', ',', path)
    # Removing or replacing other unwanted characters. Add more as needed.
    path = re.sub(r'[^a-zA-Z0-9_\-./]', '_', path)  # Replacing any unusual character with underscore
    return path

# Load S3 configurations from environment variables
bucket_name = os.getenv("S3_BUCKET_NAME")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize the boto3 S3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)



def monitor_and_upload(monitorfile, subdirectory):
    last_modified_time = None
    
    while True:
        # Check the file's modified time
        current_modified_time = os.path.getmtime(monitorfile)
        
        if last_modified_time is None:
            last_modified_time = current_modified_time

        # If the file has been modified since the last check
        if current_modified_time != last_modified_time:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f"{clean_path(os.path.basename(monitorfile))}_{timestamp}"
            
            # Upload to S3
            with open(monitorfile, 'rb') as file_data:
                s3_client.upload_fileobj(file_data, bucket_name, os.path.join(subdirectory, s3_key))
            
            print(f"File changed! Uploaded to S3: {s3_key}")
            
            # Update the last modified time
            last_modified_time = current_modified_time
        
        # Wait for a minute before checking again
        time.sleep(60)

    last_modified_time = None
    
    while True:
        # Check the file's modified time
        current_modified_time = os.path.getmtime(monitorfile)
        
        if last_modified_time is None:
            last_modified_time = current_modified_time

        # If the file has been modified since the last check
        if current_modified_time != last_modified_time:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            destination_file = os.path.join(destination, f"{os.path.basename(monitorfile)}_{timestamp}")
            shutil.copy2(monitorfile, destination_file)
            print(f"File changed! Copied to {destination_file}")
            
            # Update the last modified time
            last_modified_time = current_modified_time
        
        # Wait for a minute before checking again
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a file and copy it if changed.")
    parser.add_argument('--monitorfile', required=True, help="Path to the file to monitor")
    parser.add_argument('--subdirectory', required=True, help="Subdirectory in the S3 bucket where the backup should be stored")

    args = parser.parse_args()

    monitor_and_upload(args.monitorfile, args.subdirectory)
