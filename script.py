import os
import glob
import rarfile
import zipfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle

# Load token.pickle
TOKEN_PATH = 'token.pickle'
if not os.path.exists(TOKEN_PATH):
    print("Error: token.pickle file not found")
    exit(1)

with open(TOKEN_PATH, 'rb') as token:
    try:
        creds = pickle.load(token)
    except Exception as e:
        print(f"Error loading token.pickle: {e}")
        exit(1)

# Refresh token if expired
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

# Initialize Google Drive service
service = build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, folder_id="root"):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return f"Uploaded: {file.get('id')}"

def extract_file(file_name):
    extracted_files = []
    if file_name.endswith(".rar"):
        # Untuk arsip multi-volume, ekstraksi dimulai dari file part1.rar
        if file_name.endswith(".part1.rar"):
            with rarfile.RarFile(file_name) as rf:
                rf.extractall()  # Ekstrak ke direktori yang sama
                extracted_files = [os.path.join(os.getcwd(), f) for f in rf.namelist()]  # Dapatkan path lengkap
        else:
            print(f"Skipping {file_name}, it's not the first volume in a split archive.")
    elif file_name.endswith(".zip"):
        with zipfile.ZipFile(file_name, 'r') as zf:
            zf.extractall()  # Ekstrak ke direktori yang sama
            extracted_files = [os.path.join(os.getcwd(), f) for f in zf.namelist()]  # Dapatkan path lengkap
    else:
        print(f"Unsupported file type: {file_name}")
        return []
    return extracted_files

if __name__ == "__main__":
    # Get all RAR/ZIP files in the current directory
    archive_files = glob.glob("*.rar") + glob.glob("*.zip")
    if not archive_files:
        print("No archive files found to extract.")
        exit(1)

    print(f"Found {len(archive_files)} archive files: {archive_files}")

    # Extract and upload each file
    for archive in archive_files:
        print(f"Extracting {archive}...")
        extracted_files = extract_file(archive)

        if not extracted_files:
            print(f"No files extracted from {archive}. Skipping upload.")
            continue

        print(f"Uploading extracted files from {archive} to Google Drive...")
        for extracted_file in extracted_files:
            if os.path.exists(extracted_file):
                link = upload_to_drive(extracted_file)
                print(f"Uploaded {extracted_file}: {link}")
            else:
                print(f"Error: {extracted_file} does not exist.")
