import os
import base64
import requests
import time
from fastapi import APIRouter, Depends, HTTPException, Query
import cryptography.fernet as fernet
from src.database.models import OAuthTokens, Users
from src.schemas.users import UserOutSchema
from src.auth.jwthandler import get_current_user
from typing import Optional
from datetime import datetime
from fastapi.responses import RedirectResponse

from tortoise.exceptions import DoesNotExist

from pybaseball import statcast_batter 
from pybaseball import playerid_lookup
import pandas as pd
import requests
import bs4
from io import BytesIO
import tempfile 
import os 
import numpy as np
os.environ['SDL_AUDIODRIVER'] = 'dummy'
# id = playerid_lookup('trout', 'mike')['key_mlbam'][0]
# print(id)

def get_mp4s(player_id, date):
    data = statcast_batter(date, date, player_id)
    # Get the first row
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
async def get_oauth_tokens(player_id: int, date: str ):
    if not player_id:
        return {"error": "No id provided"} 
    if not date:
        return {"error": "No date provided"}
    
    try:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
    except:
        print('using orignal date', date)
    try:
        token_data = {
            "id": player_id,
            'pitches': get_mp4s(player_id, date)
        }
        return token_data
    except DoesNotExist:
        raise HTTPException(status_code=200, detail="OAuth token not found for the current user")


@router.get("/baseball/players/")
async def get_players(name: Optional[str] = None):
    if not name:
        return {"error": "No name provided"}
    
    names = name.split()
    print('received name', names)
    if len(names) == 1:
        last_name = names[0]
        print(last_name)
        try:
            s =  playerid_lookup(last_name, fuzzy=True)
            print(s)
            print(s.columns)
            cleaned_df = s.dropna()
            cleaned_df = cleaned_df.sort_values(by='mlb_played_last', ascending=False)

            resp = cleaned_df.to_dict('records')
            print(resp)
            return resp
        except Exception as e:
            return {"error": e}
    elif len(names) > 1:
        last_name = names[-1]
        first_name = " ".join(names[:-1])
        print(last_name, first_name)
        s =  playerid_lookup(last_name, first_name, fuzzy=True)
        cleaned_df = s.dropna()
        cleaned_df = cleaned_df.sort_values(by='mlb_played_last', ascending=False)
        resp = cleaned_df.to_dict('records')

        print(resp)


        return resp
    else:
        return {"error": "Invalid name format"}
    


def yf_get_team_players(query, team, date=None, formatted = True):
    try:
        # Using yfpy_query to get the players for the given team
        if date is not None:
            print(date)
            players = query.get_team_roster_player_info_by_date(team.team_id, date)

        else:
            players = query.get_team_roster_by_week(team.team_id, get_current_week(query))
        if not players:
            return "⚠️ No players found for this team."
       # print(players)
        players_list = []
        on_pitchers = False 
        players_list.append("🔹 Batters 🔹") 
        if formatted == False:
            return players
        
        for player in players:
            if player.position_type == 'P':
                print(player)
            first_letter = player.name.first[0]
            display_name = f"{first_letter}. {player.name.last}"

            if "P" in player.display_position and not on_pitchers:
                on_pitchers = True
                players_list.append("🔹 Pitchers 🔹") 
            player_info = f" {player.selected_position.position}: {display_name} {player.editorial_team_abbr} - {player.display_position}"
            players_list.append(player_info)

        formatted_response = f"🏅 {team.name.decode('utf-8')  } Roster:\n" + "\n".join(players_list)
        return formatted_response
       
    except Exception as e:
        return f"❗ An error occurred: {e}"
