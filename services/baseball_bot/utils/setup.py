import os
from dotenv import load_dotenv


def get_env_vars():
    data = {}
    try:
        my_timezone = os.environ["TIMEZONE"]
    except KeyError:
        my_timezone = 'America/New_York'

    data['bot_timezone'] = my_timezone
    try:
        bot_id = os.environ["BOT_ID"]
    except KeyError:
        bot_id = 1

    bot_id = '6b5dfa374f148c64eb1e9948f5'
    if (len(str(bot_id)) <= 1 ):
        raise Exception("No messaging platform info provided")

    load_dotenv()
    yahoo_private_key = os.getenv('YAHOO_CONSUMER_KEY')
    yahoo_private_secret = os.getenv('YAHOO_CONSUMER_SECRET')

    if (not(yahoo_private_key) or not(yahoo_private_secret)):
        print("No yahoo private key or secret found")

    
    data['bot_id'] = bot_id
    data['league_id'] = os.environ.get("LEAGUE_ID", "3932")
    data['bot_type'] = os.environ.get("BOT_TYPE", "GroupMe")
    data['bot_timezone'] = my_timezone
    data['yahoo_private_key'] = yahoo_private_key
    data['yahoo_private_secret'] = yahoo_private_secret 
    data['team_names_minutes'] = os.environ.get("TEAM_NAMES_MINUTES",  30)
    data['matchups_minutes'] = os.environ.get("MATCHUPS_MINUTES",  10)
    data['feature_flags'] = os.environ.get("FEATURE_ENV_VARS",  "")
    data['backend_url'] = os.environ.get("BACKEND_URL",  "http://localhost:5000")
    data['init_msg'] = 'Bot_id: ' + str(bot_id) + ' | League_id: ' + str(data['league_id']) + ' | Bot_type: ' + data['bot_type'] + ' | Bot_timezone: ' + my_timezone +  ' |  Team_names_minutes interval: ' + str(data['team_names_minutes'])
    return data