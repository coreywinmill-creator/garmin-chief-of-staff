"""Update a pre-existing Google Drive test file using service-account credentials."""
import json, os, sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

file_id=os.environ['GARMIN_DRIVE_FILE_ID'].strip()
info=json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
creds=service_account.Credentials.from_service_account_info(info,scopes=['https://www.googleapis.com/auth/drive'])
service=build('drive','v3',credentials=creds,cache_discovery=False)
source=Path(sys.argv[1]); assert source.is_file()
media=MediaFileUpload(str(source),mimetype='application/json',resumable=False)
result=service.files().update(fileId=file_id,media_body=media,fields='id,name,modifiedTime',supportsAllDrives=True).execute()
print('Updated Drive test file:',result['name'],'at',result.get('modifiedTime'))
