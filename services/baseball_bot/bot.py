import os
import sys
from chat.groupme import GroupMe
from yahoo import yahoo_worker
from yfpy.query import YahooFantasySportsQuery
from utils.setup import get_env_vars
import threading
import logging 
import json
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_auth_dir():
    logging.info("Getting auth directory")
    script_directory = os.path.dirname(os.path.abspath(__file__))
    auth_dir = os.path.join(script_directory, "auth")
    logging.info(f"Auth directory: {auth_dir}")  # logging.info the auth directory
    return auth_dir



def yahoo_bot(function, local_data = None):
    if local_data:
        data = local_data
    else:
        data = get_env_vars()
    bot_type = data['bot_type']
    bot_id = data['bot_id']
    yahoo_league_id = data['league_id']
    yahoo_private_key = data['yahoo_private_key']
    yahoo_private_secret = data['yahoo_private_secret']

    logging.info(f'data: {data}')
    if bot_type == 'GroupMe':
        bot = GroupMe(bot_id)
    elif bot_type in ['Slack', 'Discord']:
        logging.error(f'{bot_type} not supported yet')
        sys.exit(1)

    if bot is None:
        logging.error('No bot type specified')
        sys.exit(1)

    text = ''


    logging.info("Yahoo private key and secret found")
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

    logging.info(f'Function: {function}')
    try:
        if function == "get_league_team_names":
            text = 'Team Names For League ID: ' +str(data['league_id'])
            text = text + "\n\n" +  yahoo_worker.get_league_team_names(yahoo_query)
            text = text + "\n\n" 
        if function == "get_league_matchups":
            text = 'Team Matchups For League ID: ' +str(data['league_id'])
            text = text + "\n\n" +  yahoo_worker.get_league_matchups(yahoo_query)
            text = text + "\n\n" 
        if function == "test_live":
            text = '30 Minute Task For League ID: ' +str(data['league_id'])
            text = text + "\n\n" + ' Next run in 30 minutes!'
        if function == "test_daily":
            text = 'Daily Task For League ID: ' +str(data['league_id'])
            text = text + "\n\n" + ' Next run tomorrow!'
        if function == "daily_waivers":
            text = text + "\n\n" +  yahoo_worker.get_daily_waiver_activity(yahoo_query)
        if function == "broadcast":
            try:
                text = broadcast_message
            except KeyError:
                # do nothing here, empty broadcast message
                pass
    except Exception as e:
        logging.error(f"Error: {e}")
        text = ""
    if function == "init":
        try:
            text = data["init_msg"]
        except KeyError:
            # do nothing here, empty init message
            pass
    logging.info(data)

    if text != '':
        logging.info(text)
        if (not local_data):
             bot.send_message(text)
    

#send this as an argument to the both yahoo_bot and scheduler so you can run locally without sending to groupme
data = {
    "bot_type": "GroupMe",
    "bot_id": "1234567890",
    "league_id": "51838",
    "yahoo_private_key": "",
    "yahoo_private_secret": "",
    "feature_flags": "DAILY_WAIVERS,GET_LEAGUE_MATCHUPS",
    "backend_url": "https://api.draftwarroom.com",
    "init_msg": "Bot starting..",

    "refresh_token": "",
    "token_time": 3600
    
}

def write_tokens_to_file(data):
    try:

        access_token = os.getenv('access_token')
        refresh_token = os.getenv('refresh_token')
        token_time = os.getenv('token_time')
        consumer_key = data['yahoo_private_key']
        consumer_secret = data['yahoo_private_secret']
        # Check if the environment variables were found
        if not all([access_token, refresh_token, token_time, consumer_key, consumer_secret]):
            logging.info("One or more environment variables not found")
            return

        logging.info("All environment variables found")

        # Write the tokens to a JSON file
        file_path = get_auth_dir() + '/token.json'
        with open(file_path, 'w') as f:
            json.dump({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_time': float(token_time),                
                'token_type': 'bearer',
                'guid': None,
                'consumer_key': consumer_key,
                'consumer_secret': consumer_secret
            }, f)

        logging.info("Tokens written to JSON file")

    except Exception as e:
        logging.info(f"Error in write_tokens_to_file: {e}")


if __name__ == "__main__":
    logging.info("Starting bot checking json file for tokens..")

    data = get_env_vars()
    write_tokens_to_file(data)
    logging.info("Starting scheduler")
    from utils.scheduler import scheduler

    def start_scheduler():
        scheduler()
    # Start the scheduler in a new thread
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True  # This ensures that the thread will not prevent the program from exiting
    scheduler_thread.start()

    try:
        # Continue with the main script
        yahoo_bot("init")
    except Exception as e:
        logging.error("Main script error: %s", e)

    scheduler_thread.join()  # Wait for the scheduler thread to finish if needed
    logging.info('done')
