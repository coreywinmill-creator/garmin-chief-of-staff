"""Create a private dated Garmin history archive in an explicitly configured Drive folder."""
import json,os,sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
folder=os.environ.get("GARMIN_HISTORY_DRIVE_FOLDER_ID","").strip()
if not folder: raise SystemExit("Missing GARMIN_HISTORY_DRIVE_FOLDER_ID; no archive uploaded")
info=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
creds=service_account.Credentials.from_service_account_info(
    info,scopes=["https://www.googleapis.com/auth/drive"])
service=build("drive","v3",credentials=creds,cache_discovery=False)
source=Path(sys.argv[1])
if not source.is_file(): raise SystemExit("Missing sanitized history file")
data=json.loads(source.read_text(encoding="utf-8"))
name="garmin-history-"+data["period"]["start"]+"-to-"+data["period"]["end"]+".json"
media=MediaFileUpload(str(source),mimetype="application/json",resumable=False)
result=service.files().create(body={"name":name,"parents":[folder]},
    media_body=media,fields="id,name",supportsAllDrives=True).execute()
print("Created private history archive:",result["name"])
