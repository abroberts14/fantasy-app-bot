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
from pybaseball import statcast_batter 
from pybaseball import playerid_lookup
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
        date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
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


# def get_mp4s(player_id, date):
#     data = statcast_batter(date, date, player_id)
#     # Get the first row
#     if data.empty:
#         return []
#     print(data)
#     first_row = data.iloc[0]
#     print(first_row)
#     print(data.columns)

#     # i need to use the game id from this row and batters name to give to the next function
#     game_id = first_row['game_pk']
#     batter = first_row['batter']
#     print(game_id, batter)
#     # Call the get_all_event_videos function with the game id and batter's name
#     at_bat_pitches = get_all_event_videos(game_id, batter, player_id)

#     return at_bat_pitches[batter]

# def get_video_file(play_id):
#     site = requests.get('https://baseballsavant.mlb.com/sporty-videos?playId='+ play_id)
#     soup = bs4.BeautifulSoup(site.text, features="lxml")
#     video_obj = soup.find("video", id="sporty")
#     clip_url = video_obj.find('source').get('src')
#     return clip_url

# def get_all_event_videos(game_id, batter, player_id):

#     statcast_content = requests.get("https://baseballsavant.mlb.com/gf?game_pk="+str(game_id), timeout=None).json()
#     home = statcast_content['team_home']
#     away = statcast_content['team_away']
#     home.extend(away)
#     results = {}
#     #plays = []
#     at_bat_pitches = {}
#     for i in home:
#         if i['batter'] != batter:
#             continue

#         play_id = i['play_id']
#         ab_number = i['ab_number']
#         if at_bat_pitches.get(i['batter']) is None:
#             at_bat_pitches[i['batter']] = {}
#         if at_bat_pitches.get(i['batter']).get(str(ab_number)) is None:
#             at_bat_pitches[i['batter']][str(ab_number)] = []
#         #print(at_bat_pitches)
#         # at_bat_pitches[i['batter']] = {str(ab_number): []}
#        # print(i)
#         hr = i['result'] == 'Home Run'
#         homerun_type = None 
#         homerun_count = None 
#         if (hr):
#             print('Home Run')
#             hr_content = requests.get(f"https://baseballsavant.mlb.com/leaderboard/home-runs?type=details&player_id={player_id}", timeout=None).json()
#             for x in hr_content:
#                 if (x['play_id'] == play_id):
#                     print(x)
#                     homerun_type = x['hr_cat']
#                     homerun_count = x['ct']
#                     break


#         mp4 = get_video_file(play_id)
#        # print(mp4)
#         pitch_info = i
#         pitch_info['mp4'] = mp4 
#         if homerun_count != None:
#             pitch_info['hr_cat'] = homerun_type
#             pitch_info['hr_ct'] = homerun_count
#         at_bat_pitches[i['batter']][str(ab_number)].append(pitch_info)
    
#     return at_bat_pitches





# @router.get("/baseball/pitches")
# async def get_pitches_by_id(player_id: int, date: str ):
#     print(f"Received player_id: {player_id}")
#     print(f"Received date: {date}")
#     if not player_id:
#         print("No player_id provided")
#         return {"error": "No id provided"} 
#     if not date:
#         print("No date provided")
#         return {"error": "No date provided"}
    
#     try:
#         date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
#         print(f"Converted date: {date}")
#     except:
#         print('Failed to convert date, using original date', date)
#     try:
#         print(f"Fetching mp4s for player_id: {player_id} and date: {date}")
#         token_data = {
#             "id": player_id,
#             'pitches': get_mp4s(player_id, date)
#         }
#         print(f"Returning token_data")
#         return token_data
#     except DoesNotExist:
#         print("No player found with that id")
#         raise HTTPException(status_code=200, detail="No player found with that id")





def get_missing_dates(player_id: int, start_date: str = None, end_date: str = None):
    # Determine the date range
    if not start_date or not end_date:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Generate all dates within the specified range
    num_days = (end_date - start_date).days
    all_dates = {start_date + timedelta(days=x): x for x in range(num_days)}
    try:
        # Fetch data for the given player ID within the specified date range
        data = statcast_batter(start_dt=start_date.strftime('%Y-%m-%d'), end_dt=end_date.strftime('%Y-%m-%d'), player_id=player_id)
        if data.empty:
            # Return all dates as noon timestamps if no data is fetched
            return [int((date + timedelta(hours=12)).timestamp()) for date in all_dates]

        valid_dates_strings = data['game_date'].dropna().unique().tolist()
        valid_dates_strings.sort()

        # Find missing dates by comparing sets
        valid_dates_set = set(valid_dates_strings)
        print(valid_dates_set)
        # Ensure game_date is a datetime type and normalize
        all_date_strings = [date.strftime('%Y-%m-%d') for date in all_dates]

        missing_dates = []
        try:
            for date_str in all_date_strings:
                if date_str not in valid_dates_set:
                    # Convert the date string to a datetime object
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    noon_date_obj = date_obj + timedelta(hours=12)
                    # Convert the datetime object to a Unix timestamp (seconds since epoch)
                    #print(f"Adding date: {date_str}")
                    timestamp = int(noon_date_obj.timestamp())
                    missing_dates.append(timestamp)
                    #Append missing dates
            return missing_dates
        except Exception as e: 
            print(f"Error occurred while processing data: {e}")
            return all_date_strings

    except Exception as e:
        raise ValueError(f"Failed to fetch or process data for player ID {player_id}: {str(e)}")


@router.get("/baseball/player-valid-dates/{player_id}")
async def fetch_valid_dates(player_id: int, start_date: str = Query(None), end_date: str = Query(None)):
    try:
        # Call get_missing_dates with optional start and end date parameters
        missing_dates = get_missing_dates(player_id, start_date, end_date)
        if not missing_dates:
            return []
        return missing_dates
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

    

async def find_player_data(last_name: Optional[str] = None, first_name: Optional[str] = None) -> pd.DataFrame:
    """Attempt to find player data and handle data processing."""
    try:
        conditions = []
        if last_name:
            print(f"Searching for player by last name: {last_name}")
            conditions.append(f"name_last.str.lower() == '{last_name.lower()}'")
        if first_name:
            print(f"Searching for player by first name: {first_name}")
            conditions.append(f"name_first.str.lower() == '{first_name.lower()}'")

        query_string = " or ".join(conditions)
        s = pd.read_csv(get_register_file())
        s = s.query(query_string) if conditions else pd.DataFrame()

        if s.empty:
            return s

        print(f"Received player data with {len(s)} entries.")
        s['mlb_played_last'] = pd.to_numeric(s['mlb_played_last'], errors='coerce')
        s = s.dropna().query("key_mlbam != -1")
        s = s.sort_values(by='mlb_played_last', ascending=False, na_position='last')
        return s
    except Exception as e:
        print(f"Error processing player data: {e}")
        raise ValueError(f"Failed to process data for {first_name or ''} {last_name}")

@router.get("/baseball/players/")
async def get_players(name: Optional[str] = None):
    if not name:
        print("No name provided")
        raise HTTPException(status_code=400, detail="No name provided")
    
    names = name.split()
    print(f"Received name split into: {names}")

    try:
        if len(names) == 1:
            # Search by both last and first name regardless of results
            last_name_df = await find_player_data(last_name=names[0])
            first_name_df = await find_player_data(first_name=names[0])

            # Combine the results from both searches
            combined_df = pd.concat([last_name_df, first_name_df]).drop_duplicates().reset_index(drop=True)
        elif len(names) > 1:
            last_name = names[-1]
            first_name = " ".join(names[:-1])
            combined_df = await find_player_data(last_name=last_name, first_name=first_name)
        else:
            print("Invalid name format")
            raise HTTPException(status_code=400, detail="Invalid name format")

        if combined_df.empty:
            print("No valid entries found.")
            return []
        
        # Return the best matches sorted by your criteria
        combined_df = combined_df.sort_values(by='mlb_played_last', ascending=False, na_position='last')
        combined_df = combined_df.head(20)
        resp = combined_df.to_dict('records')
        print(f"Returning response with {len(resp)} records.")
        return resp

    except ValueError as ve:
        print(ve)
        return {"error": str(ve)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



def get_register_file():
    # Get the directory of the current file
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # Join this directory with the filename
    return os.path.join(current_file_dir, 'chadwick-register.csv')

def clean_data(player_table):
    """Cleans the player table by removing rows considered 'bad data'."""
    # Convert to string and ensure trimming
    player_table['name_first'] = player_table['name_first'].astype(str).str.strip()
    player_table['name_last'] = player_table['name_last'].astype(str).str.strip()

    # Remove rows with empty first or last names
    player_table = player_table[(player_table['name_first'] != '') & (player_table['name_last'] != '')]

    # Additional checks can be added here, e.g., negative identifiers or implausible years
    return player_table



def get_closest_names(last: str, first: str, player_table: pd.DataFrame) -> pd.DataFrame:
    """Calculates similarity of first and last name provided with all players in player_table"""
    player_table = clean_data(player_table)

    filled_df = player_table.fillna("").assign(chadwick_name=lambda df: df.name_first + " " + df.name_last)
    fuzzy_matches = pd.DataFrame(
        get_close_matches(f"{first} {last}", filled_df.chadwick_name, n=5, cutoff=0)
    ).rename({0: "chadwick_name"}, axis=1)
    return fuzzy_matches.merge(filled_df, on="chadwick_name").drop("chadwick_name", axis=1)

def search(last: str, first: str = None, fuzzy: bool = False) -> pd.DataFrame:
    """Lookup playerIDs for a given player"""
    table = pd.read_csv(get_register_file())
    table = clean_data(table)

    last = last.lower().strip()
    first = (first.lower().strip() if first else "")

    if not first:
        results = table[table['name_last'] == last]
    else:
        results = table[(table['name_last'] == last) & (table['name_first'] == first)]

    results = results.reset_index(drop=True)

    if len(results) == 0 and fuzzy:
        print("No identically matched names found! Returning the 5 most similar names.")
        results = get_closest_names(last=last, first=first, player_table=table)

    print("found ", len(results), " players")

    return results.head(20)


def find_player_id(last: str, first: str = None, fuzzy: bool = False) -> pd.DataFrame:
    """Lookup playerIDs (MLB AM, bbref, retrosheet, FG) for a given player

    Args:
        last (str, required): Player's last name.
        first (str, optional): Player's first name. Defaults to None.
        fuzzy (bool, optional): In case of typos, returns players with names close to input. Defaults to False.

    Returns:
        pd.DataFrame: DataFrame of playerIDs, name, years played
    """
    return search(last, first, fuzzy)




@router.get("/baseball/players/my-players", dependencies=[Depends(get_current_user)])
async def get_my_players(current_user: UserOutSchema = Depends(get_current_user)):
    try:
        print('looking for yahooo batters')
        # Get player IDs for each batter
        batters = []
        players = await Player.filter(user_id=current_user.id).all()
        if len(players) == 0:
            await sync_players(current_user)
            players = await Player.filter(user_id=current_user.id).all()
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
        
        # Fetch all current players from the database for the user
        existing_players = await Player.filter(user_id=current_user.id).all()
        existing_player_names = {player.full_name for player in existing_players}
        
        # Set of names from the fetched batters
        fetched_player_names = set(players['batters'])

        # Determine players not in the fetched list
        players_to_deactivate = existing_player_names - fetched_player_names

        # Update existing players' status to inactive if they are not in the fetched players list
        if players_to_deactivate:
            await Player.filter(user_id=current_user.id, full_name__in=players_to_deactivate).delete()
        # Get player IDs for each batter
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
                player_id_df = find_player_id(last, first, True)
                player_id = int(player_id_df.iloc[0]['key_mlbam'])
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
                batters.append({'name': name, 'user_id': -1, 'error': str(e)})
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
                print(player)
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
        print('token data', token_data)
        file_path = 'token.json'
        with open(file_path, 'w') as f:
            json.dump(token_data, f)
        with open('private.json', 'w') as f:
            json.dump(keys, f)
    except Exception as e:
        print(e)