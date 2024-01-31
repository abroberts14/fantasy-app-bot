from yfpy import Data
from yfpy.logger import get_logger
from yfpy.query import YahooFantasySportsQuery
from dotenv import load_dotenv
from pathlib import Path
import sys
import json
import os 
sys.path.insert(1, os.path.abspath('.'))
if os.environ.get("LOCAL_ENV") is not None:
    from services.baseball_bot.chat.groupme import GroupMe
else:
    from chat.groupme import GroupMe

project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

print(project_dir)
class Yahoo_Legends_Chatbot():
    def __init__(self):
        #TODO - Fetch from 'bots' table, does not yet exist. 
        #id - auto increment and pk
        #user_id - fk to users table
        #bot_id - string
        #league_id - string
        self.league_id = os.getenv('yahoo_league_id', '21217')
        self.bot_id = os.getenv('groupme_bot_id', '6b5dfa374f148c64eb1e9948f5')
        self.groupMeMessenger =  GroupMe(self.bot_id)
        self.env_setup()
        self.yahoo_query = YahooFantasySportsQuery(
            self.auth_dir,
            self.league_id,
            "mlb",
            offline=False,
            all_output_as_json_str=False,
            consumer_key=self.key,
            consumer_secret=self.secret
        )
        self.yahoo_query.game_id = self.yahoo_query.get_game_key_by_season(2023)

    def env_setup(self):
        project_dir = Path(__file__).parent
        sys.path.insert(0, str(project_dir))

        # load .env file in order to read local environment variables
        load_dotenv(dotenv_path=project_dir / "auth" / ".env")
        # set directory location of private.json for authentication
        auth_dir = project_dir / "auth"
        self.auth_dir = auth_dir
        # set target directory for data output
        data_dir = Path(__file__).parent / "output"
        self.data_dir = data_dir
        # create YFPY Data instance for saving/loading data
        self.data = Data(data_dir)
        with open(auth_dir / 'private.json') as f:
            data = json.load(f)
            self.key = data.get('key')
            self.secret = data.get('secret')

        return auth_dir
    
    def get_league_teams(self):
        return self.yahoo_query.get_league_teams()

    def get_league_team_names(self):
        league_teams = self.get_league_teams()
        team_names = ''
        for team in league_teams:
            team_info = team.clean_data_dict()
            print(team_info)
            tm_name = str(team_info.get('name'))
            team_names = team_names + tm_name + ' \n'
        return team_names
    
    def run_bot(self):
        self.groupMeMessenger.send_message(self.get_league_team_names())
        return True



if __name__=="__main__":
    bot = Yahoo_Legends_Chatbot()
    bot.run_bot()

#curl -X POST -d '{"bot_id": "6b5dfa374f148c64eb1e9948f5", "text": "Hello world"}' -H 'Content-Type: application/json' https://api.groupme.com/v3/bots/post
