import os
import sys
from chat.groupme import GroupMe
from yahoo import yahoo_worker
from yfpy.query import YahooFantasySportsQuery
from utils.setup import get_env_vars
import threading

def get_auth_dir():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, "auth")



def yahoo_bot(function):
    data = get_env_vars()
    print(data)
    bot_type = data['bot_type']
    bot_id = data['bot_id']
    yahoo_league_id = data['league_id']
    yahoo_private_key = data['yahoo_private_key']
    yahoo_private_secret = data['yahoo_private_secret']

    if bot_type == 'GroupMe':
        bot = GroupMe(bot_id)
    elif bot_type in ['Slack', 'Discord']:
        print(f'{bot_type} not supported yet')
        sys.exit(1)

    if bot is None:
        print('No bot type specified')
        sys.exit(1)

    text = ''

    
    if (not(yahoo_private_key) or not(yahoo_private_secret)):
        print("No yahoo private key or secret found")
        
        yahoo_query = YahooFantasySportsQuery(
            get_auth_dir(),
            yahoo_league_id,
            "mlb",
            offline=False,
            all_output_as_json_str=False,
        )
    else:
        yahoo_query = YahooFantasySportsQuery(
            get_auth_dir(),
            yahoo_league_id,
            "mlb",
            offline=False,
            all_output_as_json_str=False,
            consumer_key=yahoo_private_key,
            consumer_secret=yahoo_private_secret
        )
    yahoo_query.game_id = yahoo_query.get_game_key_by_season(2024)

    #accept broadcasts from the API
    try:
        broadcast_message = data['broadcast_message']
    except KeyError:
        broadcast_message = None


    if function == "get_league_team_names":
        text = 'Team Names For League ID: ' +str(data['league_id'])
        text = text + "\n\n" +  yahoo_worker.get_league_team_names(yahoo_query)
        text = text + "\n\n" + ' Next run in '+str(data['team_names_minutes'])+' minutes!'
    if function == "get_league_matchups":
        text = 'Team Matchups For League ID: ' +str(data['league_id'])
        text = text + "\n\n" +  yahoo_worker.get_league_matchups(yahoo_query)
        text = text + "\n\n" + ' Next run in '+str(data['matchups_minutes'])+' minutes!'
    elif function == "broadcast":
        try:
            text = broadcast_message
        except KeyError:
            # do nothing here, empty broadcast message
            pass
    elif function == "init":
        try:
            text = data["init_msg"]
            text = 'Team Matchups For League ID: ' +str(data['league_id'])
            text = text + "\n\n" +  yahoo_worker.get_league_matchups(yahoo_query)
            text = text + "\n\n" + ' Next run in '+str(data['matchups_minutes'])+' minutes!'
        except KeyError:
            # do nothing here, empty init message
            pass
    else:
        text = "Something bad happened. HALP"
    print(data)

    if text != '':
        print(text)
        bot.send_message(text)

if __name__ == "__main__":
    print("Starting bot")
    from utils.scheduler import scheduler

    def start_scheduler():
        scheduler()
    # Start the scheduler in a new thread
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.start()

    # Continue with the main script
    yahoo_bot("init")
    print('done')