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
    print(f"Received name: {name}")
    if not name:
        print("No name provided")
        return {"error": "No name provided"}
    
    names = name.split()
    print(f"Split names: {names}")
    if len(names) == 1:
        print(f"Looking up player id for last name: {names[0]}")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await asyncio.get_running_loop().run_in_executor(executor, sync_lookup_player, names[0])
        return result
    elif len(names) > 1:
        first_name = " ".join(names[:-1])
        last_name = names[-1]
        print(f"Looking up player id for last name: {last_name} and first name: {first_name}")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await asyncio.get_running_loop().run_in_executor(executor, sync_lookup_player, last_name, first_name)
        return result
    else:
        print("Invalid name format")
        return {"error": "Invalid name format"}

@router.get("/baseball/players-old/")
async def get_players(name: Optional[str] = None):
    print(f"Received name: {name}")
    if not name:
        print("No name provided")
        return {"error": "No name provided"}
    
    names = name.split()
    print(f"Split names: {names}")
    try:
        if len(names) == 1:
            last_name = names[0]
            print(f"Last name: {last_name}")
            try:
                print(f"Looking up player id for last name: {last_name}")
                s =  playerid_lookup(last_name, fuzzy=True)
                print(f"Received player id lookup result: {s}")
                cleaned_df = s.dropna()
                cleaned_df = cleaned_df.sort_values(by='mlb_played_last', ascending=False)
                resp = cleaned_df.to_dict('records')
                print(f"Returning response: {resp}")
                return resp
            except Exception as e:
                print(f"Error occurred: {e}")
                return {"error": e}
        elif len(names) > 1:
            last_name = names[-1]
            first_name = " ".join(names[:-1])
            print(f"Last name: {last_name}, First name: {first_name}")
            try:
                s =  playerid_lookup(last_name, first_name, fuzzy=True)
                print(f"Received player id lookup result: {s}")
                cleaned_df = s.dropna()
                print('cleaned_df')
                cleaned_df = cleaned_df.sort_values(by='mlb_played_last', ascending=False)
                print('sorted cleaned')
                resp = cleaned_df.to_dict('records')
                print(f"Returning response: {resp}")
                return resp
            except Exception as e:
                print(f"Error occurred: {e}")
                return {"error": e}
        else:
            print("Invalid name format")
            return {"error": "Invalid name format"}
    except Exception as e:
        print(f"Error occurred: {e}")
        return {"error": e}