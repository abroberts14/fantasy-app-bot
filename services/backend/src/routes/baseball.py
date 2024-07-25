import logging
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd
import statsapi
from fastapi import APIRouter, Depends, HTTPException, Query
from pybaseball import statcast_batter_percentile_ranks
from src.auth.jwthandler import get_current_user
from src.database.models import Player
from src.routes.oauth import require_oauth_token
from src.schemas.users import UserOutSchema
from src.utils.baseball_utils import (
    fetch_multiple_player_stats,
    fetch_player_stats,
    get_mp4s,
    get_player_dates,
    get_player_name,
)
from src.utils.yahoo_utils import get_user_batters

os.environ["SDL_AUDIODRIVER"] = "dummy"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/baseball/pitches")
async def get_pitches_by_id(player_id: int, date: str):
    """Endpoint to retrieve pitches by player ID and date."""
    if not player_id:
        logger.error("No player_id provided")
        return {"error": "No player_id provided"}
    if not date:
        logger.error("No date provided")
        return {"error": "No date provided"}

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except:
        print("Failed to convert date, using original date", date)

    date_str = date_obj.strftime("%Y-%m-%d")
    pitches = get_mp4s(player_id, date_str)
    return {"id": player_id, "pitches": pitches}


@router.get("/baseball/get-player-percentiles/{player_id}")
async def get_percentiles_by_player_id(player_id: int):
    try:
        data = statcast_batter_percentile_ranks("2024")
        print("Total records found:", len(data))

        # Convert player_id to int if it's passed as string
        player_id = int(player_id)

        # Filter the DataFrame for the specific player ID
        player_data = data[data["player_id"] == player_id]

        # Check if the player_data DataFrame is not empty (i.e., the player was found)
        if not player_data.empty:
            # Convert DataFrame row to dictionary for JSON response
            player_info = player_data.iloc[0].to_dict()
            # replace all nan values with none
            player_info = {
                k: v if pd.notnull(v) else None for k, v in player_info.items()
            }
            print(f"Player info: {player_info}")
            return player_info
        else:
            print(f"No data found for player ID: {player_id}")

            return {}
    #  raise HTTPException(status_code=404, detail=f"No data found for player ID: {player_id}")
    except ValueError:
        # Handle the case where the conversion of player_id to int fails
        raise HTTPException(
            status_code=400,
            detail="Invalid player ID provided. Player ID must be an integer.",
        )
    except Exception:
        return {}


@router.post("/baseball/get-multiple-player-stats")
async def get_multiple_player_stats(player_ids: List[int]):
    try:
        player_stats = fetch_multiple_player_stats(player_ids)
        return player_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/baseball/get-player-name/{player_id}")
async def get_player_name_by_id(player_id: int):
    try:
        return get_player_name(player_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
        # General exception handling (e.g., data fetching issues, parsing issues)
    # raise HTTPException(status_code=500, detail=str(e))


@router.get("/baseball/get-player-stats/{player_id}")
async def get_player_stats_by_id(player_id: int):
    try:
        return fetch_player_stats(player_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
        # General exception handling (e.g., data fetching issues, parsing issues)
    # raise HTTPException(status_code=500, detail=str(e))


@router.get("/baseball/get-player-dates/{player_id}")
async def fetch_valid_dates(
    player_id: int, start_date: str = Query(None), end_date: str = Query(None)
):
    try:
        # Call get_missing_dates with optional start and end date parameters
        return get_player_dates(player_id, start_date, end_date)
    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


@router.get("/baseball/players/")
async def get_players(name: Optional[str] = None):
    if not name:
        print("No name provided")
        raise HTTPException(status_code=400, detail="No name provided")

    try:
        matches = []
        for player in statsapi.lookup_player(name):
            print(player)
            if name.lower() in player["fullFMLName"].split()[1].lower():
                print("skipping due to middle name ", player["fullFMLName"])
                continue
            else:
                matches.append(
                    {
                        "name_first": player["firstName"],
                        "name_last": player["lastName"],
                        "name": player["fullName"],
                        "key_mlbam": player["id"],
                    }
                )

        # get the first 20 matches
        matches = matches[:20]

        # for each player, get their latest valid date from get_player_dates and sort it so most recent player is first
        filtered_matches = []
        for player in matches:
            player_dates = get_player_dates(player["key_mlbam"])
            print(f"player dates: {player_dates}")
            recent_date = player_dates["latest_valid_date"]
            print(recent_date)
            if recent_date:
                player["latest_valid_date"] = recent_date
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


@router.get("/baseball/players/my-players", dependencies=[Depends(require_oauth_token)])
async def get_my_players(current_user: UserOutSchema = Depends(get_current_user)):
    try:
        print("looking for yahooo batters")
        # Get player IDs for each batter
        batters = []
        print("current user id: ", current_user.id)
        players = await Player.filter(user_id=current_user.id).all()
        print("length of players: ", len(players))
        if len(players) == 0:
            print("no players found, syncing")
            return await sync_players(current_user)
            # players = await Player.filter(user_id=current_user.id).all()
        for player in players:
            try:
                print(
                    f"Searching for player ID for {player.last_name} {player.first_name}"
                )
                batters.append({"name": player.full_name, "key_mlbam": player.mlb_id})
            except Exception as e:
                print(f"Error occurred while searching for player ID: {e}")
                batters.append({"name": "", "user_id": -1, "error": str(e)})
    except Exception as e:
        print(f"Error retrieving batters: {e}")
        return {"players": {"batters": [], "pitchers": [], "error": str(e)}}

    print(f"Returning batters: {batters}")
    return {"players": {"batters": batters, "pitchers": []}}


@router.get(
    "/baseball/players/sync_players", dependencies=[Depends(require_oauth_token)]
)
async def sync_players(current_user: UserOutSchema = Depends(get_current_user)):
    try:
        print("Starting the synchronization process for yahoo batters.")
        print(f"Current user: {current_user.username}")
        players = await get_user_batters(current_user.id)
        print(f"Retrieved players from Yahoo: {players}")
        existing_players = await Player.filter(user_id=current_user.id).all()
        print(f"Existing players in database: {existing_players}")
        existing_player_names = {player.full_name for player in existing_players}
        print(f"Names of existing players: {existing_player_names}")

        # Set of names from the fetched batters
        fetched_player_names = set(players["batters"])
        print(f"Fetched player names from Yahoo: {fetched_player_names}")

        # Determine players not in the fetched list
        players_to_deactivate = existing_player_names - fetched_player_names
        print(f"Players to deactivate (not in fetched list): {players_to_deactivate}")

        # Update existing players' status to inactive if they are not in the fetched players list
        if players_to_deactivate:
            print(f"Deactivating players: {players_to_deactivate}")
            await Player.filter(
                user_id=current_user.id, full_name__in=players_to_deactivate
            ).delete()
        batters = []
        for name in players["batters"]:
            try:
                player_name_split = name.split(" ")
                if len(player_name_split) == 1:
                    print(f"Skipping {name} due to insufficient name parts.")
                    continue
                first = player_name_split[0]
                last = " ".join(player_name_split[1:])
                print(f"Processing player: First Name - {first}, Last Name - {last}")

                print(f"Attempting to find MLB ID for {name}")
                player_matches = statsapi.lookup_player(name)
                if len(player_matches) == 0:
                    print(f"No player matches found for {name}")
                    continue
                for idx, i in enumerate(player_matches):
                    print(f"Match {idx}: {i['fullName']}")
                    if i["fullName"] == "Jackson Merrill":
                        print(i)
                    if idx > 3:
                        break

                    # if i["fullName"] == name:
                    #     player_id = i["id"]
                    #     break

                player_id = statsapi.lookup_player(name)[0]["id"]

                print(f"Found MLB ID {player_id} for player {name}")
                batters.append({"name": name, "key_mlbam": player_id})
                player, created = await Player.get_or_create(
                    user_id=current_user.id,
                    full_name=name,
                    defaults={
                        "mlb_id": player_id,
                        "first_name": first,
                        "last_name": last,
                    },
                )
                if created:
                    print(f"Created new player record for {name}")
                else:
                    print(f"Updated existing player record for {name}")
                player.user_id = current_user.id
                player.mlb_id = player_id
                await player.save()
            except Exception as e:
                print(f"Error occurred while processing player {name}: {e}")
                # batters.append({'name': name, 'user_id': -1, 'error': str(e)})
    except Exception as e:
        print(f"Error during the sync operation: {e}")
        return {"players": [], "error": str(e)}

    print(
        f"Successfully synced players for {current_user.username}. Total players synced: {len(batters)}"
    )
    return {"players": {"batters": batters, "pitchers": []}}
