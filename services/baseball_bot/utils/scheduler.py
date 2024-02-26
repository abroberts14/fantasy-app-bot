from apscheduler.schedulers.blocking import BlockingScheduler
from utils.setup import get_env_vars
from bot import yahoo_bot
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import requests
from datetime import datetime, timedelta

def get_schedule(backend_url):
    url = f"{backend_url}/global-features"
    print(url)
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        schedule_dict = {}
        for item in data:
            name = item.pop('name')
            item.pop('id')
            item.pop('global_features')
            schedule_dict[name] = item
        return schedule_dict
    else:
        print(f"Failed to get schedule. Status code: {response.status_code}")
        return None


def parse_feature_flags(feature_flags_str):
    flags = {}
    for flag in feature_flags_str.split(','):
        flags[flag] = True
    return flags

def scheduler():
    print('starting scheduler 2')
    data = get_env_vars()
    print(data)

    feature_flags = parse_feature_flags(data['feature_flags'])
    print(feature_flags)
    schedule_dict = get_schedule(data['backend_url'])
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15 * 60})

    for job_name, timing in schedule_dict.items():
        print(job_name)
        s = data['feature_flags'].split(',') 
        print(s)
        if job_name.upper() not in data['feature_flags'].split(','):
            print(f"Skipping job: {job_name} as it is not enabled in feature_flags")
            continue

        if timing.get('live', False):
            trigger = IntervalTrigger(minutes=30)
        else:
            day_of_week = 'mon,tue,wed,thu,fri,sat,sun' if timing['day'] == 'all' else timing['day'].capitalize()
            trigger = CronTrigger(day_of_week=day_of_week, hour=timing['hour'], minute=timing['minute'], 
                                  start_date=datetime.now(), end_date=datetime.now() + timedelta(days=730), 
                                  timezone='UTC')

        sched.add_job(yahoo_bot, trigger, [job_name], id=job_name, replace_existing=True)
        print(f"Added job: {job_name} with trigger {trigger} ")

    print("Ready!")
    sched.start()
    print('done')