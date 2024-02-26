from apscheduler.schedulers.blocking import BlockingScheduler
from utils.setup import get_env_vars
from bot import yahoo_bot
from apscheduler.triggers.interval import IntervalTrigger
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


def scheduler():
    print('starting scheduler')
    data = get_env_vars()
    print(data)
    features = data['feature_flags']

    schedule_dict = get_schedule(data['backend_url'])
    print(schedule_dict)
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15 * 60})
    for job_name, timing in schedule_dict.items():
        sched.add_job(
            yahoo_bot, 'cron', [job_name], id=job_name,
            day_of_week='mon', hour=timing['hour'], minute=timing['minute'],
            start_date=datetime.now(), end_date=datetime.now() + timedelta(days=730),
            timezone='UTC',  # Replace with your timezone
            replace_existing=True
        )
        print(f"Added job: {job_name} at {timing['hour']}:{timing['minute']}")
    # sched.add_job(yahoo_bot, 'cron', ['get_league_team_names'], id='team_names',
    #               day_of_week='mon', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
    #               timezone=data['bot_timezone'], replace_existing=True)
    # sched.add_job(yahoo_bot, 'interval', minutes=int(data['team_names_minutes']), args=['get_league_team_names'], id='team_names',
    #           timezone=data['bot_timezone'], replace_existing=True)
    sched.add_job(yahoo_bot, 'interval', minutes=int(data['matchups_minutes']), args=['get_league_matchups'], id='league_matchups',
              timezone=data['bot_timezone'], replace_existing=True)

    print("Ready!")
    sched.start()
    print('done')