from apscheduler.schedulers.blocking import BlockingScheduler
from utils.setup import get_env_vars
from bot import yahoo_bot
from apscheduler.triggers.interval import IntervalTrigger

def scheduler():
    data = get_env_vars()
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15 * 60})
    # sched.add_job(yahoo_bot, 'cron', ['get_league_team_names'], id='team_names',
    #               day_of_week='mon', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
    #               timezone=data['bot_timezone'], replace_existing=True)
    sched.add_job(yahoo_bot, 'interval', minutes=data['team_names_minutes'], args=['get_league_team_names'], id='team_names',
              timezone=data['bot_timezone'], replace_existing=True)
    print("Ready!")
    sched.start()
