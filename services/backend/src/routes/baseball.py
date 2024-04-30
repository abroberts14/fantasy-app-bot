import os
import requests
from fastapi import APIRouter, HTTPException, BackgroundTasks
import concurrent.futures

from typing import Optional
from datetime import datetime
from tortoise.exceptions import DoesNotExist

from pybaseball import statcast_batter 
from pybaseball import playerid_lookup
import pandas as pd
import requests
import bs4
import os 
import asyncio
from difflib import get_close_matches
import numpy as np
os.environ['SDL_AUDIODRIVER'] = 'dummy'
# id = playerid_lookup('trout', 'mike')['key_mlbam'][0]
# print(id)

def get_mp4s(player_id, date):
    data = statcast_batter(date, date, player_id)
    # Get the first row
    if data.empty:
        return []
    print(data)
    first_row = data.iloc[0]
    print(first_row)
    print(data.columns)

    # i need to use the game id from this row and batters name to give to the next function
    game_id = first_row['game_pk']
    batter = first_row['batter']
    print(game_id, batter)
    # Call the get_all_event_videos function with the game id and batter's name
    at_bat_pitches = get_all_event_videos(game_id, batter, player_id)

    return at_bat_pitches[batter]

def get_video_file(play_id):
    site = requests.get('https://baseballsavant.mlb.com/sporty-videos?playId='+ play_id)
    soup = bs4.BeautifulSoup(site.text, features="lxml")
    video_obj = soup.find("video", id="sporty")
    clip_url = video_obj.find('source').get('src')
    return clip_url

def get_all_event_videos(game_id, batter, player_id):

    statcast_content = requests.get("https://baseballsavant.mlb.com/gf?game_pk="+str(game_id), timeout=None).json()
    home = statcast_content['team_home']
    away = statcast_content['team_away']
    home.extend(away)
    results = {}
    #plays = []
    at_bat_pitches = {}
    for i in home:
        if i['batter'] != batter:
            continue

        play_id = i['play_id']
        ab_number = i['ab_number']
        if at_bat_pitches.get(i['batter']) is None:
            at_bat_pitches[i['batter']] = {}
        if at_bat_pitches.get(i['batter']).get(str(ab_number)) is None:
            at_bat_pitches[i['batter']][str(ab_number)] = []
        #print(at_bat_pitches)
        # at_bat_pitches[i['batter']] = {str(ab_number): []}
       # print(i)
        hr = i['result'] == 'Home Run'
        homerun_type = None 
        homerun_count = None 
        if (hr):
            print('Home Run')
            hr_content = requests.get(f"https://baseballsavant.mlb.com/leaderboard/home-runs?type=details&player_id={player_id}", timeout=None).json()
            for x in hr_content:
                if (x['play_id'] == play_id):
                    print(x)
                    homerun_type = x['hr_cat']
                    homerun_count = x['ct']
                    break


        mp4 = get_video_file(play_id)
       # print(mp4)
        pitch_info = i
        pitch_info['mp4'] = mp4 
        if homerun_count != None:
            pitch_info['hr_cat'] = homerun_type
            pitch_info['hr_ct'] = homerun_count
        at_bat_pitches[i['batter']][str(ab_number)].append(pitch_info)
    
    return at_bat_pitches



router = APIRouter()



@router.get("/baseball/pitches")
async def get_pitches_by_id(player_id: int, date: str ):
    print(f"Received player_id: {player_id}")
    print(f"Received date: {date}")
    if not player_id:
        print("No player_id provided")
        return {"error": "No id provided"} 
    if not date:
        print("No date provided")
        return {"error": "No date provided"}
    
    try:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
        print(f"Converted date: {date}")
    except:
        print('Failed to convert date, using original date', date)
    try:
        print(f"Fetching mp4s for player_id: {player_id} and date: {date}")
        token_data = {
            "id": player_id,
            'pitches': get_mp4s(player_id, date)
        }
        print(f"Returning token_data")
        return token_data
    except DoesNotExist:
        print("No player found with that id")
        raise HTTPException(status_code=200, detail="No player found with that id")

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