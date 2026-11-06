"""Read-only Garmin collector: optional API features are capability-detected."""
import inspect, json, os
from datetime import date, timedelta, datetime
from pathlib import Path
from garmin_personal_api import GarminPersonalApiClient, PersonalApiAuthenticator
ROOT=Path(os.environ.get('GARMIN_COS_HOME',Path.home()/'GarminChiefOfStaff'))
OUT=ROOT/'reports';OUT.mkdir(parents=True,exist_ok=True)
key=os.environ.get('GARMIN_PERSONAL_API_KEY','').strip()
if not key: raise SystemExit('Missing Garmin API key')

def optional(client, name, variants, results, unavailable):
    method=getattr(client,name,None)
    if not callable(method):
        unavailable[name]='not_supported_by_installed_client';return
    try: sig=inspect.signature(method)
    except (ValueError,TypeError):
        unavailable[name]='signature_unavailable';return
    for args,kwargs in variants:
        try: sig.bind(*args,**kwargs)
        except TypeError: continue
        try:
            value=method(*args,**kwargs)
            results[name]=value
        except Exception as e:
            unavailable[name]=type(e).__name__
        return
    unavailable[name]='no_compatible_signature'

def main():
    today=date.today(); start=today-timedelta(days=30); t=today.isoformat(); s=start.isoformat()
    data={'generated_at_local':datetime.now().astimezone().isoformat(), 'period':{'start':s,'end':t},'sources':{},'errors':{},'unsupported':{},'note':'Raw local data: private; do not upload to Drive.'}
    with PersonalApiAuthenticator() as auth: token=auth.obtain_token(key)
    with GarminPersonalApiClient(token.access_token) as client:
        basic={
            'sleep_today':lambda:client.get_daily_sleep(t),
            'steps_7d':lambda:client.get_daily_steps((today-timedelta(days=7)).isoformat(),t),
            'stress_7d':lambda:client.get_daily_stress((today-timedelta(days=7)).isoformat(),t),
            'activities_30d':lambda:client.search_activities(start=0,limit=100,start_date=s,end_date=t),
        }
        for label,fn in basic.items():
            try:data['sources'][label]=fn()
            except Exception as exc:data['errors'][label]=type(exc).__name__
        # Only invoke installed client methods with compatible signatures. No fabricated endpoints.
        dates=[((t,),{}), ((),{'date':t}), ((),{'calendar_date':t}), ((),{'date_str':t})]
        ranges=[((s,t),{}),((),{'start_date':s,'end_date':t}), ((),{'start':s,'end':t})]
        candidates={
  'get_daily_hrv':dates,
  'get_daily_hrv_summaries':ranges,
  'get_daily_body_battery':ranges,
  'get_hrv_data':dates,'get_hrv':dates,'get_body_battery':dates,
          'get_training_readiness':dates,'get_training_status':dates,
          'get_recovery_time':dates,'get_vo2max':dates,'get_max_metrics':dates,
          'get_daily_heart_rate':dates,'get_heart_rates':dates,
          'get_daily_intensity_minutes':dates,'get_daily_spo2':dates,
          'get_daily_respiration':dates,'get_daily_blood_pressure':dates,
          'get_daily_hydration':dates,'get_daily_calories':dates,
          'get_daily_sleep':[], 'get_daily_steps':ranges,
        }
        for name,variants in candidates.items():
            if not variants:continue
            optional(client,name,variants,data['sources'],data['unsupported'])
        # Activity detail methods: cap requests to 30 to limit rate/volume.
        activities=data['sources'].get('activities_30d') or []
        if isinstance(activities,dict):activities=activities.get('activities',[])
        details=[]
        for a in activities[:30]:
            if not isinstance(a,dict):continue
            aid=a.get('activityId')
            if not aid:continue
            record={'activityId':aid}
            for name in ('get_activity','get_activity_details','get_activity_splits','get_activity_hr_in_timezones','get_activity_exercise_sets'):
                method=getattr(client,name,None)
                if not callable(method):continue
                try:
                    inspect.signature(method).bind(aid)
                    record[name]=method(aid)
                except (TypeError,ValueError):continue
                except Exception as exc:record[name+'_error']=type(exc).__name__
            if len(record)>1:details.append(record)
        data['sources']['activity_details_30d']=details
    for name in ('latest.json',f'garmin-{t}.json'):
        (OUT/name).write_text(json.dumps(data,indent=2,default=str),encoding='utf-8')
        for name in ('get_daily_hrv', 'get_daily_hrv_summaries', 'get_daily_body_battery'):
    value = data['sources'].get(name)
    print('METRIC FORMAT:', name, 'type=', type(value).__name__,
          'keys=', list(value.keys()) if isinstance(value, dict) else 'not a dictionary')
    print('Collected:',', '.join(data['sources']));print('Unsupported:',', '.join(data['unsupported']))
    print('Local raw report:',OUT/'latest.json')
if __name__=='__main__':main()
