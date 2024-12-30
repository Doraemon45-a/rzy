import os
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path, folder_id):
    # Jika file_path adalah direktori, telusuri dan upload semua file
    if os.path.isdir(file_path):
        for root, dirs, files in os.walk(file_path):
            for file_name in files:
                full_file_path = os.path.join(root, file_name)
                media = MediaFileUpload(full_file_path, resumable=True)
                # Asumsikan ada fungsi untuk meng-upload media ke Google Drive
                link = upload_media_to_google_drive(media, folder_id, full_file_path)
                print(f'Uploaded: {full_file_path}, Link: {link}')
    else:
        # Jika file_path adalah file, langsung upload
        media = MediaFileUpload(file_path, resumable=True)
        link = upload_media_to_google_drive(media, folder_id, file_path)
        print(f'Uploaded: {file_path}, Link: {link}')

# Contoh penggunaan
folder_id = '1BqeRm09e4HkxOahklm2f8YU6qHkvIkPr'
extracted_file = '/path/ke/direktori/atau/file'
upload_to_drive(extracted_file, folder_id)
