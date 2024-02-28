from yfpy.query import YahooFantasySportsQuery
from datetime import datetime, timedelta, timezone
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import os

def get_league_teams(qry):
        return qry.get_league_teams()

def get_league_team_names(qry):
    league_teams = get_league_teams(qry)
    team_names = ''
    for team in league_teams:
        team_info = team.clean_data_dict()
        tm_name = str(team_info.get('name'))
        team_names += tm_name + ' \n'
    return team_names

def get_league_matchups(qry):
      return yf_get_league_matchups(qry)

def yf_get_league_matchups(qry):
    current_week = get_current_week(qry)
    league_matchups = qry.get_league_scoreboard_by_week(current_week).matchups
    formatted_matchups = ""

    max_team_name_length = max(len(matchup.teams[0].name.decode('utf-8')) for matchup in league_matchups if len(matchup.teams) == 2)
    max_score_length = 5  # width of "0.00"

    for matchup in league_matchups:
        teams = matchup.teams

        if len(teams) == 2:  # Ensure there are two teams in the matchup
            team_1 = teams[0]
            team_2 = teams[1]

            # Extract team names and scores
            team_1_name = team_1.name.decode('utf-8')
            team_1_score = team_1.team_points.total
            team_2_name = team_2.name.decode('utf-8')
            team_2_score = team_2.team_points.total

            formatted_matchups += f"{team_1_name.ljust(max_team_name_length)} {str(team_1_score).rjust(max_score_length)} - {str(team_2_score).ljust(max_score_length)} {team_2_name}\n"

    # Calculate the length of the longest line
    max_line_length = max(len(line) for line in formatted_matchups.split('\n'))

    # Add the "Score Update" text in the middle
    score_update_text = "Score Update:"
    formatted_matchups = score_update_text.center(max_line_length - len(score_update_text) // 2) + "\n \n" + formatted_matchups

    return formatted_matchups

def get_teams_info(teams):
    """
    Gathers information about each team, including the team key and the number of moves made.
    
    Args:
        teams (list[Team]): A list of Team objects

    Returns:
        dict: A dictionary with team keys as keys and a tuple of (number of moves made, max moves allowed) as values.
    """
    teams_info = {}
    team_names = {}
    for team in teams:
        team_key = team.team_key
        number_of_moves = team.number_of_moves
        teams_info[team_key] = number_of_moves
        team_names[team_key] = team.name
        team_names[team_key] = team.name.decode('utf-8')  # Decode the UTF-8 encoded byte string

    return teams_info, team_names

def get_daily_waiver_activity(qry):
    waiver_activity = qry.get_league_transactions()
    teams = qry.get_league_teams()
    teams_info, team_names = get_teams_info(teams)
    formatted_activity = ''
    
    # Get yesterday's date for the report
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    yesterday_date = yesterday.date()
    formatted_activity += f"Transaction Report For {yesterday_date}:\n\n"

    # Initialize a defaultdict for storing transactions
    team_transactions = defaultdict(lambda: defaultdict(list))
    
    # Process each transaction
    for transaction in waiver_activity:
        transaction_time = datetime.fromtimestamp(transaction.timestamp, timezone.utc)
        if transaction_time.date() == yesterday_date and transaction.type == "add/drop":
            for player in transaction.players:
                player_data = player.transaction_data
                team_key = player_data.destination_team_key if player_data.type == "add" else player_data.source_team_key
                action = "Added" if player_data.type == "add" else "Dropped"
                player_info = f"{player.name.full} - ({player.editorial_team_abbr} - {player.display_position})"
                if player_data.type == "add":
                    if player_data.source_type == "waivers":
                        player_info += " [Off Waivers]"
                    if transaction.faab_bid is not None:
                        player_info += f" ($ {transaction.faab_bid})"
                team_transactions[team_key][action].append(player_info)

    if len(team_transactions) == 0:
        return ""
    # Format the transactions for each team
    for team_key, actions in team_transactions.items():
        if team_key in teams_info:
            moves_made = teams_info[team_key]
            team_info = f"{team_names.get(team_key, 'Unknown Team')} (#{moves_made})"
        else:
            continue  # Skip if team_key not found in teams_info

        formatted_activity += f"{team_info}\n"
        for action, players in actions.items():
            formatted_activity += f"{action} "
            formatted_activity += ", ".join(players)
            formatted_activity += "\n"
        formatted_activity += "\n"

    return formatted_activity

def get_auth_dir():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, "auth")

consumer_key= "dj0yJmk9NTZlWXZjdlY1SUZhJmQ9WVdrOVkxWnZjemRJVVhFbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTgz"
consumer_secret= "e656aa67c44c49a1c201c4f984ef6b83fb09fe73"


def get_current_week(qry):
    return qry.get_league_info().current_week
if __name__ == '__main__':
    yahoo_query = YahooFantasySportsQuery(
        r'C:\Users\aaron\Documents\dev\fastapi-vue\services\baseball_bot\auth',
        '3932',
        "mlb",
        offline=False,
        all_output_as_json_str=False,
        # consumer_key=consumer_key,
        # consumer_secret=consumer_secret
    )
    yahoo_query.game_id = yahoo_query.get_game_key_by_season(2024)

    #print(get_daily_waiver_activity(yahoo_query))
    print(get_league_matchups(yahoo_query))