import os
import glob
import rarfile
import zipfile
from googleapiclient.discovery import build
from googleapiclation.http import MediaFileUpload
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
    """
    Meng-upload file ke Google Drive ke folder yang ditentukan
    :param file_path: Path file yang akan di-upload
    :param folder_id: ID folder di Google Drive, defaultnya adalah 'root'
    :return: URL untuk mengunduh file
    """
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # Set the file permissions to allow anyone with the link to view it
    file_id = file.get('id')
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(fileId=file_id, body=permission).execute()

    # Generate a sharable link to the file
    link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    return link

def extract_file(file_name):
    extracted_files = []
    if file_name.endswith(".rar"):
        # Handle multi-volume RAR extraction, start with part1.rar
        if file_name.endswith(".part1.rar"):
            with rarfile.RarFile(file_name) as rf:
                rf.extractall()  # Extract to the current directory
                extracted_files = [os.path.join(os.getcwd(), f) for f in rf.namelist()]  # Get full paths
        else:
            print(f"Skipping {file_name}, it's not the first volume in a split archive.")
    elif file_name.endswith(".zip"):
        with zipfile.ZipFile(file_name, 'r') as zf:
            zf.extractall()  # Extract to the current directory
            extracted_files = [os.path.join(os.getcwd(), f) for f in zf.namelist()]  # Get full paths
    else:
        print(f"Unsupported file type: {file_name}")
        return []
    return extracted_files

def check_and_create_folder(folder_name="Uploaded Files"):
    # Check if folder exists on Google Drive
    results = service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                                   fields="files(id, name)").execute()
    folders = results.get('files', [])
    if not folders:
        # Folder does not exist, create it
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    else:
        # Folder exists, return folder ID
        return folders[0].get('id')

if __name__ == "__main__":
    # Get all RAR/ZIP files in the current directory
    archive_files = glob.glob("*.rar") + glob.glob("*.zip")
    if not archive_files:
        print("No archive files found to extract.")
        exit(1)

    print(f"Found {len(archive_files)} archive files: {archive_files}")

    # Check and create Google Drive folder if needed
    folder_id = check_and_create_folder()

    # Extract and upload each file
    for archive in archive_files:
        print(f"Extracting {archive}...")
        extracted_files = extract_file(archive)

        if not extracted_files:
            print(f"No files extracted from {archive}. Skipping upload.")
            continue

        print(f"Uploading extracted files from {archive} to Google Drive...")

        # Upload each extracted file to Google Drive
        for extracted_file in extracted_files:
            if os.path.exists(extracted_file):
                print(f"Uploading {extracted_file}...")
                link = upload_to_drive(extracted_file, folder_id)
                print(f"File uploaded successfully. Download it at: {link}")
            else:
                print(f"Error: {extracted_file} does not exist.")
