import requests
from requests.auth import HTTPBasicAuth
import zipfile, os
from io import BytesIO
from xml.etree import ElementTree as ET
from tqdm import tqdm
import re

from dotenv import load_dotenv

load_dotenv()

def clean_path(path):
    # Decoding URL-encoded characters
    path = re.sub(r'%2c', ',', path)
    # Removing or replacing other unwanted characters. Add more as needed.
    path = re.sub(r'[^a-zA-Z0-9_\-./]', '_', path)  # Replacing any unusual character with underscore
    return path
    
webdav_url = os.getenv("webdavURL")
username =  os.getenv("webdavusername")
password = os.getenv("webdavpassword")

headers = {'Depth': '1'}
response = requests.request('PROPFIND', webdav_url, headers=headers, auth=HTTPBasicAuth(username, password))

if response.status_code == 207:
    # Parse the Multi-Status XML response to extract file names
    root = ET.fromstring(response.content)
    namespaces = {'d': 'DAV:'}
    
    # Extract file names with ".zip" extension
    file_names = [elem.text for elem in root.findall(".//d:href", namespaces) if elem.text.endswith('.zip')]
    
    if not file_names:
        print("No ZIP files found in the folder.")
    else:
        for zip_file_name in tqdm(file_names):
            zip_response = requests.get(zip_file_name, auth=HTTPBasicAuth(username, password))

            if zip_response.status_code == 200:
                # Create a subfolder based on the ZIP file name
                subfolder_name = os.path.join("crypts", os.path.splitext(os.path.basename(zip_file_name))[0])
                subfolder_name = clean_path(subfolder_name)
                os.makedirs(subfolder_name, exist_ok=True)
                
                # Extract the ZIP file's content into the subfolder
                with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
                    for file_info in z.infolist():
                        file_data = z.read(file_info.filename)
                        file_path = os.path.join(subfolder_name, file_info.filename)
                        
                        # Write the file data to the subfolder
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
            else:
                print(f"Failed to download ZIP file '{zip_file_name}'. Status code: {zip_response.status_code}")
else:
    print(f"Failed to list folder contents. Status code: {response.status_code}")