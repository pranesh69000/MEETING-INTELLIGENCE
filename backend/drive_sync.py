import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveManager:
    def __init__(self, credentials_file="credentials.json"):
        self.creds = None
        self.credentials_file = credentials_file
        self.service = None
        
        # Check for token.json (cached auth)
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        # If no valid token, user must login
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except:
                    self.creds = None 
            
            # If still no creds, we need to run the flow
            # For a headless backend, this might open a browser window on the server (machine)
            # Since this is a desktop app, it's fine.
            if not self.creds and os.path.exists(credentials_file):
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())
        
        if self.creds:
            self.service = build('drive', 'v3', credentials=self.creds)

    def upload_file(self, file_path, folder_name="Meeting_Intelligence_Logs"):
        if not self.service:
            return {"error": "Authentication failed. Check credentials.json"}
            
        filename = os.path.basename(file_path)
        
        # 1. Check if folder exists, create if not
        folder_id = None
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if not items:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
        else:
            folder_id = items[0]['id']
            
        # 2. Upload File
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, mimetype='text/plain')
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return {
            "file_id": file.get('id'),
            "link": file.get('webViewLink')
        }
