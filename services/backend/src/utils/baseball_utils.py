from datetime import datetime, timedelta
from typing import List

import bs4
import pandas as pd
import statsapi
from pybaseball import batting_stats, batting_stats_range
from pybaseball.enums.fangraphs.month import FangraphsMonth
from pytz import timezone
from src.utils.pybaseball_utils import (
    custom_statcast_batter,
    fg_batting_data_extended,
    find_player_fangraphs_id,
    split_request,
)
from src.utils.utils import fetch_url


def get_video_file(play_id):
    """Fetch video file URL from a play ID."""
    url = f"https://baseballsavant.mlb.com/sporty-videos?playId={play_id}"
    response = fetch_url(url)
    if response:
        soup = bs4.BeautifulSoup(response.text, "lxml")
        video_obj = soup.find("video", id="sporty")
        if video_obj and video_obj.find("source"):
            return video_obj.find("source")["src"]
    return None


def fetch_homerun_details(play_id, player_id):
    """Fetch details for homeruns."""
    url = "https://baseballsavant.mlb.com/leaderboard/home-runs"
    params = {"type": "details", "player_id": player_id}
    response = fetch_url(url, params=params)
    if response:
        data = response.json()
        for record in data:
            if record["play_id"] == play_id:
                return {"hr_cat": record["hr_cat"], "hr_ct": record["ct"]}
    return {}


def get_all_event_videos(game_id, batter, player_id, extra_data={}):
    """Retrieve all event videos for a game, filtering by the batter."""
    url = f"https://baseballsavant.mlb.com/gf?game_pk={game_id}"
    response = fetch_url(url)
    at_bat_pitches = {}
    if response:
        data = response.json()
        for event in data.get("team_home", []) + data.get("team_away", []):
            if event["batter"] != batter:
                continue
            play_id = event["play_id"]
            ab_number = event["ab_number"]
            pitches = at_bat_pitches.setdefault(batter, {}).setdefault(
                str(ab_number), []
            )
            mp4 = get_video_file(play_id)
            pitch_info = event
            pitch_info["mp4"] = mp4
            if event["result"] == "Home Run":
                homerun_details = fetch_homerun_details(play_id, player_id)
                if homerun_details:
                    pitch_info.update(homerun_details)
            if extra_data:
                pitch_info.update(extra_data)
            pitches.append(pitch_info)
    return at_bat_pitches


def get_mp4s(player_id, date):
    """Fetch MP4 URLs for a player on a specific date."""
    print(f"fetching mp4s for player {player_id} on date {date}")
    data = custom_statcast_batter(date, date, player_id)
    # Get the first row
    if data.empty:
        print(f"no data found for player {player_id} on date {date}")
        return []
    first_row = data.iloc[0]
    # drop any nan columns
    first_row.dropna(inplace=True)
    game_id = first_row["game_pk"]
    batter = first_row["batter"]
    print(f"batter: {batter}")
    # Call the get_all_event_videos function with the game id and batter's name
    try:
        extra_data = {
            "bat_speed": first_row["bat_speed"],
            "swing_length": first_row["swing_length"],
        }
    except:
        extra_data = {}
    at_bat_pitches = get_all_event_videos(game_id, batter, player_id, extra_data)

    return at_bat_pitches[batter]


def get_player_dates(
    player_id: int,
    start_date: str = None,
    end_date: str = None,
    latest_date: bool = False,
):
    # Determine the
    # date range
    print(f"player id: {player_id}, start date: {start_date}, end date: {end_date}")

    try:
        gamelog = statsapi.get(
            "people",
            {
                "personIds": player_id,
                "hydrate": "stats(group=[hitting],type=[gameLog])",
            },
        )
        try:
            # Filter splits where plateAppearances is greater than 0
            est = timezone("US/Eastern")
            today = datetime.now(est).date()
            valid_dates = []
            for split in gamelog["people"][0]["stats"][0]["splits"]:
                split_date = datetime.strptime(split["date"], "%Y-%m-%d").date()
                # print(f"Date: {split['date']}, Plate Appearances: {split['stat']['plateAppearances']}")
                if split["stat"]["plateAppearances"] > 0 and split_date != today:
                    valid_dates.append(split["date"])
            valid_dates.sort(reverse=True)  # Sort dates in descending order
        except Exception as e:
            print("error getting any valid dates", e)
            valid_dates = []
        if start_date is not None and end_date is not None:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            # Generate all dates within the specified range
            num_days = (end_date - start_date).days + 1
            # one print statement to output all parameters in one line for debugging
            all_dates = {start_date + timedelta(days=x): x for x in range(num_days)}
            all_date_strings = [date.strftime("%Y-%m-%d") for date in all_dates]
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
        resp = {
            "disabled_dates": invalid_dates_set,
            "latest_valid_date": latest_valid_date,
            "valid_dates": valid_dates,
            "latest_disabled_date": latest_disabled_date,
        }

        return resp

    except Exception as e:
        print("error getting player dates ", e)
        # make this double qoutes
        resp = {
            "disabled_dates": [],
            "latest_valid_date": None,
            "valid_dates": [],
            "latest_disabled_date": None,
            "error": str(e),
        }
        return resp


def fetch_player_stats(player_id: int, batting_data: pd.DataFrame):
    try:
        player_fg_id = find_player_fangraphs_id(player_id)
        print(
            f"fetch_player_stats: player_id: {player_id}, player_fg_id: {player_fg_id}"
        )
        print(
            f"searching for player_id: {player_id} in batting_data length of {len(batting_data)}"
        )
        player_id_fangraphs = int(player_fg_id)
        # print our the row that has the name of sean murphy
        try:
            player_data = batting_data[batting_data["IDfg"] == player_id_fangraphs]
        except Exception as e:
            print(f"error getting player data: {e}")

        # loop through the entire data frame and look for the name Marcus Semien and print the row

        if not player_data.empty:
            player_info = player_data.iloc[0].to_dict()
            # Remove null or nan values
            player_info = {
                k: round(v, 3) if isinstance(v, float) else v
                for k, v in player_info.items()
                if pd.notnull(v)
            }
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
    today = datetime.now()
    print(f"Fetching player stats as of {today}")

    # Fetch data for the current year
    print("Fetching data for the current year")
    data_all = batting_stats(str(today.year), qual=5)
    print(f"Data for the current year fetched: {len(data_all)} records")

    # Fetch data for the last 7 days
    start_dt_7 = today - timedelta(days=7)
    print(
        f"Fetching data from {start_dt_7.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
    )
    data_7 = fg_batting_data_extended(
        str(today.year), month="LAST_SEVEN", ind=0, qual=5
    )
    print(f"Data for the last 7 days fetched: {len(data_7)} records")
    data_14 = fg_batting_data_extended(
        str(today.year), month="LAST_FOURTEEN", ind=0, qual=5
    )
    print(f"Data for the last 14 days fetched: {len(data_14)} records")
    data_30 = fg_batting_data_extended(
        str(today.year), month="LAST_THIRTY", ind=0, qual=5
    )
    print(f"Data for the last 30 days fetched: {len(data_30)} records")
    # Fetch data for the last 14 days
    # start_dt_14 = today - timedelta(days=14)
    # print(
    #     f"Fetching data from {start_dt_14.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
    # )
    # data_14 = batting_stats_range(
    #     start_dt=start_dt_14.strftime("%Y-%m-%d"),
    #     end_dt=today.strftime("%Y-%m-%d"),
    # )
    # print(f"Data for the last 14 days fetched: {len(data_14)} records")

    # # Fetch data for the last 30 days
    # start_dt_30 = today - timedelta(days=30)
    # print(
    #     f"Fetching data from {start_dt_30.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
    # )
    # data_30 = batting_stats_range(
    #     start_dt=start_dt_30.strftime("%Y-%m-%d"),
    #     end_dt=today.strftime("%Y-%m-%d"),
    # )
    # print(f"Data for the last 30 days fetched: {len(data_30)} records")

    for player_id in player_ids:
        results[player_id] = {}
        try:
            # print(f"Fetching stats for player ID: {player_id}")
            # Store stats for all time periods
            results[player_id]["all"] = fetch_player_stats(player_id, data_all)
            results[player_id]["7"] = fetch_player_stats(player_id, data_7)
            results[player_id]["14"] = fetch_player_stats(player_id, data_14)
            results[player_id]["30"] = fetch_player_stats(player_id, data_30)
            # print(f"Stats stored for player ID: {player_id}")
        except Exception as e:
            results[player_id] = {"error": str(e)}
            print(f"Error fetching stats for player ID: {player_id}: {e}")

    return results


# https://www.fangraphs.com/leaders-legacy.aspx?pos=all&stats=bat&lg=all&qual=y&type=8&season=2023&month=1&season1=2023&ind=0&team=0&rost=0&age=0&filter=&players=0
# https://www.fangraphs.com/leaders-legacy.aspx?pos=all&stats=bat&lg=all&qual=y&type=8&season=2024&month=1&season1=2024&ind=0&team=0&rost=0&age=0&filter=&players=0
