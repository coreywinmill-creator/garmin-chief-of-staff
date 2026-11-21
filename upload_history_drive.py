"""Update an existing user-owned Drive JSON file; service accounts have no My Drive quota."""
import json,os,sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

file_id=os.environ.get("GARMIN_HISTORY_DRIVE_FILE_ID","").strip()
if not file_id:
    raise SystemExit("Missing GARMIN_HISTORY_DRIVE_FILE_ID; cannot create files in My Drive with service account")
info=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
creds=service_account.Credentials.from_service_account_info(
    info,scopes=["https://www.googleapis.com/auth/drive"])
service=build("drive","v3",credentials=creds,cache_discovery=False)
source=Path(sys.argv[1])
if not source.is_file(): raise SystemExit("Missing sanitized history file")
data=json.loads(source.read_text(encoding="utf-8"))
if not isinstance(data.get("activities"),list) or not data.get("period"):
    raise SystemExit("Invalid history payload")
meta=service.files().get(fileId=file_id,fields="id,name,mimeType",supportsAllDrives=True).execute()
if meta.get("mimeType")!="application/json":
    raise SystemExit("Target file is not JSON; refusing to overwrite")
media=MediaFileUpload(str(source),mimetype="application/json",resumable=False)
result=service.files().update(fileId=file_id,media_body=media,
    fields="id,name,size",supportsAllDrives=True).execute()
print("Updated existing private history archive:",result["name"],"activities:",len(data["activities"]))
