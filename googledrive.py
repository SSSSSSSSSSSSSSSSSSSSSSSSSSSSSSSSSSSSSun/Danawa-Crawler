from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'key.json'
DIECTORY_ID = '1QX52j2Zmbv78hMruka6D45zXK2i1qx5q'

def connectDrive():
	creds = None

	try:
		if os.path.exists(TOKEN_FILE):
			creds = Credentials.from_authorized_user_file(TOKEN_FILE,SCOPES)
	except:
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				# 재발급
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(TOKEN_FILE, SCOPES)
				creds = flow.run_local_server(port=0)
			with open(TOKEN_FILE, 'w') as file:
				file.write(creds.to_json())

	return build('drive', 'v3', credentials=creds)


def uploadFile(service, DATA_NAME):

	query = f"'{DIECTORY_ID}' in parents and name='{DATA_NAME}'"
	response = service.files().list(q=query).execute()

	files = response.get('files', [])
	file_name = f"crawl_data/{DATA_NAME}"

	if not files:
		file_metadata = {'name': DATA_NAME, 'parents':[DIECTORY_ID]}
		media = MediaFileUpload(file_name,mimetype='text/csv')
		service.files().create(body=file_metadata, media_body=media, fields='id').execute()

	else:
		media = MediaFileUpload(file_name,mimetype='text/csv')
		service.files().update(fileId=files[0]['id'], media_body=media).execute()