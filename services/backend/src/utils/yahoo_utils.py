import json
import os
from datetime import datetime

from src.routes import oauth
from yfpy import YahooFantasySportsQuery


def del_token():
    # Delete token.json
    try:
        os.remove("token.json")
    except FileNotFoundError:
        print("token.json not found")
    except Exception as e:
        print(f"Error occurred while deleting token.json: {e}")

    try:
        os.remove("private.json")
    except FileNotFoundError:
        print("token.json not found")
    except Exception as e:
        print(f"Error occurred while deleting token.json: {e}")


def yf_get_current_user_team(query):
    try:
        print("getting league teams")
        teams = query.get_league_teams()
        print(f"teams: {teams}")
        for team in teams:
            if team.is_owned_by_current_login:
                print(f"team: {team}")
                return team

        return None  # No team is owned by the current login

    except Exception as e:
        return f"❗ An error occurred: {e}"


def yf_get_team_players(query, team=None, date=None, formatted=True):
    try:
        print("Starting to fetch team players.")
        if team is None:
            print("No team provided, fetching current user's team.")
            team = yf_get_current_user_team(query)
            if team is None:
                print("No team owned by current user.")
                return "No team owned by current user."
            else:
                print(f"Using team: {team.name} with ID {team.team_id}")
        else:
            print(f"Team provided: {team.name} with ID {team.team_id}")

        # Using yfpy_query to get the players for the given team
        if date is not None:
            print(f"Fetching players for date: {date}")
            players = query.get_team_roster_player_info_by_date(team.team_id, date)
        else:
            chosen_date = datetime.now().strftime("%Y-%m-%d")
            print(f"No date provided, using current date: {chosen_date}")
            players = query.get_team_roster_player_info_by_date(
                team.team_id, chosen_date
            )

        if not players:
            print("No players found for this team.")
            return "⚠️ No players found for this team."

        players_list = []
        for player in players:
            print(
                f"Processing player: {player.name.first} {player.name.last}, Position type: {player.position_type}"
            )
            if player.position_type == "B":
                players_list.append(f"{player.name.first} {player.name.last}")
                print(f"Added player to list: {player.name.first} {player.name.last}")

        print("Finished fetching team players.")
        return players_list

    except Exception as e:
        print(f"An error occurred while fetching team players: {e}")
        return f"❗ An error occurred: {e}"


async def get_user_batters(user_id: int):
    print(user_id)
    await setup_yahoo_oauth(user_id)
    keys = {
        "consumer_key": os.getenv("YAHOO_CLIENT_ID"),
        "consumer_secret": os.getenv("YAHOO_CLIENT_SECRET"),
    }
    yahoo_query = YahooFantasySportsQuery(
        ".",
        "51838",
        "mlb",
        offline=False,
        all_output_as_json_str=False,
        consumer_key=keys["consumer_key"],
        consumer_secret=keys["consumer_secret"],
    )
    players = yf_get_team_players(yahoo_query)
    return {"batters": players}


async def setup_yahoo_oauth(user_id: int):
    print("setting up yahoo oauth")
    try:
        oauth_token = await oauth.get_oauth_token_by_id(user_id)
        access_token = oauth_token["access_token"]
        refresh_token = oauth_token.get("refresh_token")
        token_type = oauth_token.get("token_type")
        expires_in = oauth_token.get("expires_in")
        keys = {
            "consumer_key": os.getenv("YAHOO_CLIENT_ID"),
            "consumer_secret": os.getenv("YAHOO_CLIENT_SECRET"),
        }
        print(expires_in)
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": token_type,
            "token_time": expires_in,
            "consumer_key": keys["consumer_key"],
            "consumer_secret": keys["consumer_secret"],
        }
        file_path = "token.json"
        with open(file_path, "w") as f:
            json.dump(token_data, f)
        with open("private.json", "w") as f:
            json.dump(keys, f)
    except Exception as e:
        print(e)
