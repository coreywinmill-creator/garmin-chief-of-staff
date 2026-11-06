"""Explicit allowlist export. No GPS, routes, profile data, names, IDs or tokens."""
import json,sys
from datetime import datetime
from pathlib import Path
raw=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
sources=raw.get('sources',{})
def get(obj,*names):
    if not isinstance(obj,dict):return None
    for n in names:
        if obj.get(n) is not None:return obj[n]
def numeric(v):return v if isinstance(v,(float,int)) and not isinstance(v,bool) else None
def safe(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    return None
sleep=sources.get('sleep_today') or {}
if isinstance(sleep,dict) and isinstance(sleep.get('dailySleepDTO'),dict):sleep=sleep['dailySleepDTO']
score=get(sleep,'sleepScores') or {}
overall=get(score,'overall') or {}
secs=get(sleep,'sleepTimeSeconds')
summary={'schema_version':2,'generated_at_local':raw.get('generated_at_local'),'period':raw.get('period'),
 'sleep':{'date':get(sleep,'calendarDate'),'duration_minutes':round(secs/60) if numeric(secs) else None,
          'score':get(overall,'value'),'score_label':get(overall,'qualifierKey'),
          'deep_minutes':round(sleep['deepSleepSeconds']/60) if numeric(get(sleep,'deepSleepSeconds')) else None,
          'rem_minutes':round(sleep['remSleepSeconds']/60) if numeric(get(sleep,'remSleepSeconds')) else None,
          'average_sleep_stress':get(sleep,'avgSleepStress'),'average_sleep_heart_rate':get(sleep,'avgHeartRate')},
 'steps_7d':[],'stress_7d':[],'activities_30d':[],'additional_metrics':{},
 'availability':{'failed':list(raw.get('errors',{})),'unsupported':list(raw.get('unsupported',{}))},
 'privacy':'Allowlisted metrics only; no GPS, route, activity IDs, profile identifiers, names or credentials.'}
for a in sources.get('steps_7d') or []:
    if isinstance(a,dict):summary['steps_7d'].append({'date':get(a,'calendarDate'),'steps':get(a,'totalSteps')})
for a in sources.get('stress_7d') or []:
    if isinstance(a,dict):summary['stress_7d'].append({'date':get(a,'calendarDate'),'stress_level':get(get(a,'values') or {},'overallStressLevel')})
acts=sources.get('activities_30d') or []
if isinstance(acts,dict):acts=acts.get('activities',[])
for a in acts[:100]:
    if not isinstance(a,dict):continue
    duration=get(a,'duration')
    typ=get(a,'activityType') or {}
    summary['activities_30d'].append({'date':get(a,'startTimeLocal'),'type':get(typ,'typeKey'),
      'duration_minutes':round(duration/60,1) if numeric(duration) else None,
      'distance_meters':get(a,'distance'),'average_hr':get(a,'averageHR'),'max_hr':get(a,'maxHR'),
      'average_speed_mps':get(a,'averageSpeed'),'max_speed_mps':get(a,'maxSpeed'),
      'calories':get(a,'calories'),'training_load':get(a,'activityTrainingLoad'),
      'aerobic_effect':get(a,'aerobicTrainingEffect'),'anaerobic_effect':get(a,'anaerobicTrainingEffect'),
      'elevation_gain_meters':get(a,'elevationGain'),'average_cadence':get(a,'averageRunningCadenceInStepsPerMinute')})
# Export scalar summary fields only from optional sources, never whole raw objects.
allowed={
 'get_daily_hrv':('calendarDate','weeklyAvg','lastNightAvg','lastNight5MinHigh','status'),
 'get_daily_hrv_summaries':('weeklyAvg','lastNightAvg','status'),
 'get_daily_body_battery':('bodyBatteryValue','chargedValue','drainedValue'),
 'get_daily_heart_rate':('calendarDate','restingHeartRate','minHeartRate','maxHeartRate'),
}
for source,keys in allowed.items():
    value=sources.get(source)
    if isinstance(value,dict):
        subset={k:safe(value[k]) for k in keys if k in value and safe(value[k]) is not None}
        if subset:summary['additional_metrics'][source]=subset
# Export privacy-filtered HRV measurements
hrv = sources.get('get_daily_hrv') or {}
if isinstance(hrv, dict):
    hrv_summary = hrv.get('hrvSummary') or {}

    if isinstance(hrv_summary, dict):
        keys = (
            'calendarDate',
            'weeklyAvg',
            'lastNightAvg',
            'lastNight5MinHigh',
            'status'
        )

        summary['additional_metrics']['hrv'] = {
            k: hrv_summary[k]
            for k in keys
            if k in hrv_summary and safe(hrv_summary[k]) is not None
        }

# Export HRV trends without account identifiers
hrv_data = sources.get('get_daily_hrv_summaries') or {}
if isinstance(hrv_data, dict):
    records = hrv_data.get('hrvSummaries') or []

    if isinstance(records, list):
        summary['additional_metrics']['hrv_trend'] = [
            {
                k: record[k]
                for k in ('calendarDate', 'weeklyAvg', 'lastNightAvg', 'status')
                if k in record and safe(record[k]) is not None
            }
            for record in records[-14:]
            if isinstance(record, dict)
        ]

# Export daily Body Battery totals
battery = sources.get('get_daily_body_battery') or []

if isinstance(battery, list):
    summary['additional_metrics']['body_battery'] = [
        {
            k: record[k]
            for k in ('date', 'charged', 'drained')
            if k in record and safe(record[k]) is not None
        }
        for record in battery[-7:]
        if isinstance(record, dict)
    ]
Path(sys.argv[2]).write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print('Privacy-reduced summary updated:',sys.argv[2])
