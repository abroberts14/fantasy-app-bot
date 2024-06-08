import io
import os
import requests
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.encoders import jsonable_encoder

import concurrent.futures

from typing import Optional, Tuple
from datetime import datetime, timedelta, date, timezone
from tortoise.exceptions import DoesNotExist
from src.auth.jwthandler import get_current_user
from src.schemas.users import UserOutSchema
from src.database.models import Player
from pybaseball import statcast_batter, statcast_batter_percentile_ranks
from pybaseball import playerid_lookup, batting_stats_range, batting_stats, playerid_reverse_lookup
from pybaseball import cache

import pandas as pd
import requests
import bs4
import os 
import asyncio
from difflib import get_close_matches
import numpy as np
from src.routes import oauth
from src.crud import bots
import json
import logging
import statsapi 

from yfpy.query import YahooFantasySportsQuery
from typing import List
from time import sleep
os.environ['SDL_AUDIODRIVER'] = 'dummy'
# id = playerid_lookup('trout', 'mike')['key_mlbam'][0]
# print(id)
# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
#cache.enable()


# Create a requests session for connection pooling
session = requests.Session()

def fetch_url(url, params=None):
    """ Utility function to fetch data from the given URL. """
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

def get_video_file(play_id):
    """ Fetch video file URL from a play ID. """
    url = f'https://baseballsavant.mlb.com/sporty-videos?playId={play_id}'
    response = fetch_url(url)
    if response:
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        video_obj = soup.find("video", id="sporty")
        if video_obj and video_obj.find('source'):
            return video_obj.find('source')['src']
    return None

def get_all_event_videos(game_id, batter, player_id, extra_data = {}):
    """ Retrieve all event videos for a game, filtering by the batter. """
    url = f"https://baseballsavant.mlb.com/gf?game_pk={game_id}"
    response = fetch_url(url)
    at_bat_pitches = {}
    if response:
        data = response.json()
        for event in data.get('team_home', []) + data.get('team_away', []):
            if event['batter'] != batter:
                continue
            play_id = event['play_id']
            ab_number = event['ab_number']
            pitches = at_bat_pitches.setdefault(batter, {}).setdefault(str(ab_number), [])
            mp4 = get_video_file(play_id)
            pitch_info = event
            pitch_info['mp4'] = mp4
            if event['result'] == 'Home Run':
                homerun_details = fetch_homerun_details(play_id, player_id)
                if homerun_details:
                    pitch_info.update(homerun_details)
            if extra_data:
                pitch_info.update(extra_data)
            pitches.append(pitch_info)
    return at_bat_pitches

def fetch_homerun_details(play_id, player_id):
    """ Fetch details for homeruns. """
    url = f"https://baseballsavant.mlb.com/leaderboard/home-runs"
    params = {'type': 'details', 'player_id': player_id}
    response = fetch_url(url, params=params)
    if response:
        data = response.json()
        for record in data:
            if record['play_id'] == play_id:
                return {'hr_cat': record['hr_cat'], 'hr_ct': record['ct']}
    return {}

def get_mp4s(player_id, date):
    """ Fetch MP4 URLs for a player on a specific date. """
    data = custom_statcast_batter(date, date, player_id)
    # Get the first row
    if data.empty:
        return []
    first_row = data.iloc[0]
    print(first_row)
    #drop any nan columns
    first_row.dropna(inplace=True)
    game_id = first_row['game_pk']
    batter = first_row['batter']

    # Call the get_all_event_videos function with the game id and batter's name
    try:
        extra_data = {
            'bat_speed': first_row['bat_speed'],
            'swing_length': first_row['swing_length']
        }
    except:
        extra_data = {}
    at_bat_pitches = get_all_event_videos(game_id, batter, player_id, extra_data)

    return at_bat_pitches[batter]

@router.get("/baseball/pitches")
async def get_pitches_by_id(player_id: int, date: str):
    """ Endpoint to retrieve pitches by player ID and date. """
    if not player_id:
        logger.error("No player_id provided")
        return {"error": "No player_id provided"} 
    if not date:
        logger.error("No date provided")
        return {"error": "No date provided"}
    
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except:
        print('Failed to convert date, using original date', date)

    date_str = date_obj.strftime("%Y-%m-%d")
    pitches = get_mp4s(player_id, date_str)
    return {"id": player_id, 'pitches': pitches}

def custom_statcast_batter(start_dt: Optional[str] = None, end_dt: Optional[str] = None, player_id: Optional[int] = None) -> pd.DataFrame:
    """
    Pulls statcast pitch-level data from Baseball Savant for a given batter.

    ARGUMENTS
        start_dt : YYYY-MM-DD : the first date for which you want a player's statcast data
        end_dt : YYYY-MM-DD : the final date for which you want data
        player_id : INT : the player's MLBAM ID. Find this by calling pybaseball.playerid_lookup(last_name, first_name), 
            finding the correct player, and selecting their key_mlbam.
    """
    
    new_url = 'https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=batter&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={}&game_date_lt={}&batters_lookup%5B%5D={}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&chk_stats_sweetspot_speed_mph=on&chk_stats_swing_length=on&type=details&'
    df = split_request(start_dt, end_dt, player_id, new_url)
    return df


@router.get("/baseball/get-player-percentiles/{player_id}")  
async def get_percentiles_by_player_id(player_id: int):
    try:
        data = statcast_batter_percentile_ranks('2024')
        print("Total records found:", len(data))
        
        # Convert player_id to int if it's passed as string
        player_id = int(player_id)
        
        # Filter the DataFrame for the specific player ID
        player_data = data[data['player_id'] == player_id]

        # Check if the player_data DataFrame is not empty (i.e., the player was found)
        if not player_data.empty:
            # Convert DataFrame row to dictionary for JSON response
            player_info = player_data.iloc[0].to_dict()
            # replace all nan values with none 
            player_info = {k: v if pd.notnull(v) else None for k, v in player_info.items()}
            print(f"Player info: {player_info}")
            return player_info
        else:
            print(f"No data found for player ID: {player_id}")

            return {}
          #  raise HTTPException(status_code=404, detail=f"No data found for player ID: {player_id}")
    except ValueError as e:
        # Handle the case where the conversion of player_id to int fails
        raise HTTPException(status_code=400, detail="Invalid player ID provided. Player ID must be an integer.")
    except Exception as e:
        return {}


def get_batting_data(year: str = '2024'):
    # This function fetches batting data and caches it
    return batting_stats(year)

async def batting_data_dependency(year: str = '2024'):
    return get_batting_data(year)

def fetch_player_stats(player_id: int, batting_data: pd.DataFrame):
    try:
        data = playerid_reverse_lookup([player_id], key_type='mlbam')
        player_fg_id = data[data['key_mlbam'] == player_id]['key_fangraphs'].values[0]

        print(f'player_id: {player_id}, player_fg_id: {player_fg_id}')
        # if batting_data is None:
        #     batting_data = batting_stats('2024')
        player_id_fangraphs = int(player_fg_id)
        #print our the row that has the name of sean murphy 
        player_data = batting_data[batting_data['IDfg'] == player_id_fangraphs]
        #loop through the entire data frame and look for the name Marcus Semien and print the row 
        for index, row in batting_data.iterrows():
            if row['Name'] == 'Marcus Semien':
                print(row)
        if not player_data.empty:
            player_info = player_data.iloc[0].to_dict()
            # Remove null or nan values
            player_info = {k: round(v, 3) if isinstance(v, float) else v for k, v in player_info.items() if pd.notnull(v)}
            return player_info
        else:
            print(f"No data found for player ID: {player_id}")
            
            return {}
    except ValueError as e:
        raise ValueError("Invalid player ID provided. Player ID must be an integer.")
    except Exception as e:
        return {}

def fetch_multiple_player_stats(player_ids: List[int]):
    results = {}
    data = batting_stats('2024', qual=5)

    for player_id in player_ids:
        try:
            player_stats = fetch_player_stats(player_id, data)
            results[player_id] = player_stats
        except Exception as e:
            results[player_id] = {"error": str(e)}
    return results

@router.post("/baseball/get-multiple-player-stats")
async def get_multiple_player_stats(player_ids: List[int]):
    try:
        player_stats = fetch_multiple_player_stats(player_ids)
        return player_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/baseball/get-player-stats/{player_id}")  
async def get_player_stats_by_id(player_id: int):
    try:
        return fetch_player_stats(player_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
        # General exception handling (e.g., data fetching issues, parsing issues)
       # raise HTTPException(status_code=500, detail=str(e))

# retrieve all players' batting stats for the month of May, 2017 
def split_request(start_dt: str, end_dt: str, player_id: int, url: str) -> pd.DataFrame:
	"""
	Splits Statcast queries to avoid request timeouts
	"""
	current_dt = datetime.strptime(start_dt, '%Y-%m-%d')
	end_dt_datetime = datetime.strptime(end_dt, '%Y-%m-%d')
	results = []  # list to hold data as it is returned
	player_id_str = str(player_id)
	print('Gathering Player Data')
	# break query into multiple requests
	while current_dt <= end_dt_datetime:
		remaining = end_dt_datetime - current_dt
		# increment date ranges by at most 60 days
		delta = min(remaining, timedelta(days=2190))
		next_dt = current_dt + delta
		start_str = current_dt.strftime('%Y-%m-%d')
		end_str = next_dt.strftime('%Y-%m-%d')
		# retrieve data
		data = requests.get(url.format(start_str, end_str, player_id_str))
		df = pd.read_csv(io.StringIO(data.text))
		# add data to list and increment current dates
		results.append(df)
		current_dt = next_dt + timedelta(days=1)
	return pd.concat(results)







def get_player_dates(player_id: int, start_date: str = None, end_date: str = None, latest_date: bool = False):
    # Determine the
    # date range
    print(f'player id: {player_id}, start date: {start_date}, end date: {end_date}')

    try:
        gamelog = statsapi.get('people', {'personIds': player_id, 'hydrate': f'stats(group=[hitting],type=[gameLog])'})
        try:
            # Filter splits where plateAppearances is greater than 0
            valid_dates = [
                split['date'] for split in gamelog['people'][0]['stats'][0]['splits']
                if split['stat']['plateAppearances'] > 0
            ]
            valid_dates.sort(reverse=True)  # Sort dates in descending order
        except Exception as e   :
            print("error getting any valid dates", e)
            valid_dates = []
        if start_date != None and end_date != None:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Generate all dates within the specified range
            num_days = (end_date - start_date).days + 1
             # one print statement to output all parameters in one line for debugging    
            all_dates = {start_date + timedelta(days=x): x for x in range(num_days)}
            all_date_strings = [date.strftime('%Y-%m-%d') for date in all_dates] 
            all_date_strings.sort()
            all_date_set = set(all_date_strings)
            valid_dates_set = set(valid_dates)
            invalid_dates_set = all_date_set - valid_dates_set
            latest_disabled_date = max(invalid_dates_set)
            if valid_dates:
                latest_valid_date = valid_dates[0]
            else:
                latest_valid_date = None
        else:
            all_date_set = []
            valid_dates_set = valid_dates
            invalid_dates_set = []
            latest_disabled_date = None 
            if valid_dates:
                latest_valid_date = valid_dates[0]
            else:
                latest_valid_date = None
        resp =  {
                    "disabled_dates": invalid_dates_set,
                    "latest_valid_date": latest_valid_date,
                    "valid_dates": valid_dates,
                    "latest_disabled_date": latest_disabled_date
                }
        
        return resp
      
    except Exception as e:
        print("error getting player dates ", e)
        #make this double qoutes  
        resp =  {
            "disabled_dates": [],
            "latest_valid_date": None,
            "valid_dates": [],
            "latest_disabled_date": None,
            "error": str(e)
        }
        return resp



@router.get("/baseball/get-player-dates/{player_id}")
async def fetch_valid_dates(player_id: int, start_date: str = Query(None), end_date: str = Query(None)):
    try:
        # Call get_missing_dates with optional start and end date parameters
        return get_player_dates(player_id, start_date, end_date)
    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


def sync_lookup_player(last_name: str, first_name: Optional[str] = None):
    try:
        print(f"Initiating lookup for {first_name} {last_name}")
        # Correctly use the playerid_lookup function from pybaseball library
        s = playerid_lookup(last_name, first_name, fuzzy=True)
        print(f"Lookup successful: {s}")
        cleaned_df = s.dropna()
        cleaned_df = cleaned_df.sort_values(by='mlb_played_last', ascending=False)
        return cleaned_df.to_dict('records')
    except Exception as e:
        print(f"An error occurred during lookup: {e}")
        return {"error": str(e)}

    
@router.get("/baseball/players/")
async def get_players(name: Optional[str] = None):
    if not name:
        print("No name provided")
        raise HTTPException(status_code=400, detail="No name provided")
    

    try:
        matches = []
        for player in statsapi.lookup_player(name):
            print(player)
            if name.lower() in player['fullFMLName'].split()[1].lower():
                print('skipping due to middle name ', player['fullFMLName'])
                continue
            else:
                matches.append({'name_first': player['firstName'], 'name_last': player['lastName'], 'name': player['fullName'], 'key_mlbam': player['id']})

        # get the first 20 matches 
        matches = matches[:20]

        #for each player, get their latest valid date from get_player_dates and sort it so most recent player is first
        filtered_matches = []
        for player in matches:
            player_dates = get_player_dates(player['key_mlbam'])
            print(f"player dates: {player_dates}")
            recent_date = player_dates['latest_valid_date']
            print(recent_date)
            if recent_date:
                player['latest_valid_date'] = recent_date
                filtered_matches.append(player)  # Only add players with a valid date
            else:
                print(f'skipping {player["name"]} due to no valid dates this season ')
                continue

        print(f"Returning response with {len(filtered_matches)} records.")
        return filtered_matches

    except ValueError as ve:
        print(ve)
        return {"error": str(ve)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")





@router.get("/baseball/players/my-players", dependencies=[Depends(get_current_user)])
async def get_my_players(current_user: UserOutSchema = Depends(get_current_user)):
    try:
        print('looking for yahooo batters')
        # Get player IDs for each batter
        batters = []
        players = await Player.filter(user_id=current_user.id).all()
        if len(players) == 0:
            return await sync_players(current_user)
            #players = await Player.filter(user_id=current_user.id).all()
        for player in players:
            try:
                print(f"Searching for player ID for {player.last_name} {player.first_name}")
                batters.append({'name': player.full_name, 'key_mlbam': player.mlb_id})
            except Exception as e:
                print(f"Error occurred while searching for player ID: {e}")
                batters.append({'name': '', 'user_id': -1, 'error': str(e)})
    except Exception as e:
        print(f"Error retrieving batters: {e}")
        return {'players': {"batters": [], "pitchers": [], "error": str(e)}}

    print(f"Returning batters: {batters}")
    return {'players': {"batters": batters, "pitchers": []}}

@router.get("/baseball/players/sync_players", dependencies=[Depends(get_current_user)])
async def sync_players(current_user: UserOutSchema = Depends(get_current_user)):
    try:
        print('Syncing yahoo batters for user:', current_user.username)
        players = await get_user_batters(current_user.id)
        
        existing_players = await Player.filter(user_id=current_user.id).all()
        existing_player_names = {player.full_name for player in existing_players}
        
        # Set of names from the fetched batters
        fetched_player_names = set(players['batters'])

        # Determine players not in the fetched list
        players_to_deactivate = existing_player_names - fetched_player_names

        # Update existing players' status to inactive if they are not in the fetched players list
        if players_to_deactivate:
            await Player.filter(user_id=current_user.id, full_name__in=players_to_deactivate).delete()
        batters = []
        for name in players['batters']:
            try:
                player_name_split = name.split(' ')
                first = player_name_split[0]
                last = ' '.join(player_name_split[1:])
                print("Attempting to store player in database")
                print(f"First: {first}, Last: {last}")
                # Insert or update player in database

            
                print(f"Searching for player ID for {last} {first}")
                player_id = statsapi.lookup_player(name)[0]['id']
                print(f"Found player ID: {player_id}")
                batters.append({'name': name, 'key_mlbam': player_id})
                player, created = await Player.get_or_create(
                    user_id=current_user.id, 
                    full_name=name, 
                    defaults={'mlb_id': player_id, 'first_name': first, 'last_name': last}
                )
                player.user_id = current_user.id
                player.mlb_id = player_id
                await player.save()
            except Exception as e:
                print(f"Error occurred while searching for player ID: {e}")
                #batters.append({'name': name, 'user_id': -1, 'error': str(e)})
    except Exception as e:
        print(f"Error syncing players: {e}")
        return {"players": [], "error": str(e)}

    print(f"Returning synced players for {current_user.username}: {batters}")
    return {'players': {"batters": batters, "pitchers": []}}


def del_token():   
    # Delete token.json
    try:
        os.remove("token.json")
    except FileNotFoundError:
        print("token.json not found")
    except Exception as e:
        print(f"Error occurred while deleting token.json: {e}" )

    try:
        os.remove("private.json")
    except FileNotFoundError:
        print("token.json not found")
    except Exception as e:
        print(f"Error occurred while deleting token.json: {e}" )
            
       
    
def yf_get_current_user_team(query):
    try:
        teams = query.get_league_teams()

        for team in teams:
            if team.is_owned_by_current_login:
                return team

        return None  # No team is owned by the current login

    except Exception as e:
        return f"❗ An error occurred: {e}"

def yf_get_team_players(query, team = None, date=None, formatted = True):
    try:
        if team == None:
            team = yf_get_current_user_team(query)
        # Using yfpy_query to get the players for the given team
        if date is not None:
             players = query.get_team_roster_player_info_by_date(team.team_id, date)
        else:
            chosen_date = datetime.now().strftime("%Y-%m-%d")
            players = query.get_team_roster_player_info_by_date(team.team_id, chosen_date)
        if not players:
            return "⚠️ No players found for this team."
        players_list = []
        for player in players:
            print(player.name.first, player.name.last, player.position_type)
            if player.position_type == 'B':
                players_list.append( f"{ player.name.first} {player.name.last}")
        return players_list
       
    except Exception as e:
        return f"❗ An error occurred: {e}"

async def get_user_batters(user_id: int):
    print(user_id)
    await setup_yahoo_oauth(user_id)
    keys = {
        "consumer_key": os.getenv('YAHOO_CLIENT_ID'),
        "consumer_secret": os.getenv('YAHOO_CLIENT_SECRET')
    }
    yahoo_query = YahooFantasySportsQuery(
        '.',
        '51838',
        "mlb",
        offline=False,
        all_output_as_json_str=False,
        consumer_key=keys["consumer_key"],
        consumer_secret=keys["consumer_secret"]
    )
    players = yf_get_team_players(yahoo_query)
    return {"batters": players}


async def setup_yahoo_oauth(user_id: int):
    print('setting up yahoo oauth')
    try:
        oauth_token =  await oauth.get_oauth_token_by_id(user_id)
        access_token = oauth_token['access_token']
        refresh_token = oauth_token.get('refresh_token')
        token_type = oauth_token.get('token_type')
        expires_in = oauth_token.get('expires_in')
        keys = {
            "consumer_key": os.getenv('YAHOO_CLIENT_ID'),
            "consumer_secret": os.getenv('YAHOO_CLIENT_SECRET')
        }
        print(expires_in)
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": token_type,
            "token_time": expires_in,
            "consumer_key": keys["consumer_key"],
            "consumer_secret": keys["consumer_secret"]
        }
        file_path = 'token.json'
        with open(file_path, 'w') as f:
            json.dump(token_data, f)
        with open('private.json', 'w') as f:
            json.dump(keys, f)
    except Exception as e:
        print(e)