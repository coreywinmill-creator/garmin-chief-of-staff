"""Privacy-filtered Garmin activity history export for manual GitHub Actions backfills."""
import json, os, time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from garmin_personal_api import GarminPersonalApiClient, PersonalApiAuthenticator

def clean(a):
    typ=a.get("activityType") or {}
    if not isinstance(typ,dict): typ={}
    fields={"startTimeLocal":"date","duration":"duration_seconds","distance":"distance_meters",
            "averageHR":"average_hr","maxHR":"max_hr","calories":"calories",
            "activityTrainingLoad":"training_load","aerobicTrainingEffect":"aerobic_effect",
            "anaerobicTrainingEffect":"anaerobic_effect","averageRunningCadenceInStepsPerMinute":"running_cadence"}
    out={"type":typ.get("typeKey")}
    for source,dest in fields.items():
        val=a.get(source)
        if isinstance(val,(int,float,str)) and not isinstance(val,bool):
            out[dest]=val
    return out

def main():
    days=max(31,min(int(os.environ.get("GARMIN_HISTORY_DAYS","365")),3650))
    max_pages=max(1,min(int(os.environ.get("GARMIN_HISTORY_MAX_PAGES","20")),100))
    end=datetime.now(ZoneInfo("America/New_York")).date()
    start=end-timedelta(days=days)
    key=os.environ.get("GARMIN_PERSONAL_API_KEY","").strip()
    if not key: raise SystemExit("Missing GARMIN_PERSONAL_API_KEY")
    records=[]
    with PersonalApiAuthenticator() as auth: token=auth.obtain_token(key)
    with GarminPersonalApiClient(token.access_token) as client:
        for page in range(max_pages):
            batch=client.search_activities(start=page*100,limit=100,
                start_date=start.isoformat(),end_date=end.isoformat())
            if isinstance(batch,dict): batch=batch.get("activities") or []
            if not isinstance(batch,list): raise RuntimeError("Unexpected activities response")
            records.extend(clean(a) for a in batch if isinstance(a,dict))
            print("History page",page+1,"records",len(batch))
            if len(batch)<100: break
            time.sleep(0.5)
    output=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"garmin-history.json"
    output.write_text(json.dumps({"schema_version":1,"period":{"start":start.isoformat(),
        "end":end.isoformat()},"activities":records,"count":len(records),
        "truncated":len(records)>=max_pages*100,
        "privacy":"Allowlisted activity metrics only; no GPS, names, identifiers or routes."},
        indent=2),encoding="utf-8")
    print("Sanitized historical activities:",len(records),"output:",output)
if __name__=="__main__": main()
