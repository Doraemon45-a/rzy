import os
import pickle
import sys
import rarfile
import zipfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Load token.pickle
token_path = 'token.pickle'
if not os.path.exists(token_path):
    print("Error: token.pickle file not found")
    sys.exit(1)

with open(token_path, 'rb') as token:
    try:
        creds = pickle.load(token)
    except Exception as e:
        print(f"Error loading token.pickle: {e}")
        sys.exit(1)

# If the token is expired, refresh it
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

# Build the Google Drive service
service = build('drive', 'v3', credentials=creds)

def upload_file_to_drive(file_path, folder_id):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file.get('id')
    download_link = f"https://drive.google.com/uc?id={file_id}&export=download"
    return download_link

def extract_file(file_path, extract_to):
    if rarfile.is_rarfile(file_path):
        print(f"Extracting RAR file: {file_path}")
        with rarfile.RarFile(file_path) as rf:
            rf.extractall(path=extract_to)
    elif zipfile.is_zipfile(file_path):
        print(f"Extracting ZIP file: {file_path}")
        with zipfile.ZipFile(file_path, 'r') as zf:
            zf.extractall(path=extract_to)
    else:
        print(f"Error: {file_path} is not a valid RAR or ZIP file.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]  # Path ke file RAR/ZIP
    folder_id = "1BqeRm09e4HkxOahklm2f8YU6qHkvIkPr"  # ID folder di Google Drive

    # Direktori untuk menyimpan file hasil ekstraksi
    extract_dir = "./extracted"
    os.makedirs(extract_dir, exist_ok=True)

    # Ekstrak file RAR/ZIP
    extract_file(file_path, extract_dir)

    # Upload file hasil ekstraksi ke Google Drive
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_to_upload = os.path.join(root, file)
            link = upload_file_to_drive(file_to_upload, folder_id)
            print(f"File {file_to_upload} uploaded successfully. Download it at: {link}")
