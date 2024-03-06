from yfpy.query import YahooFantasySportsQuery
from datetime import datetime, timedelta, timezone
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

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
    twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(days=1)


    # Initialize a defaultdict for storing transactions
    #team_transactions = defaultdict(lambda: defaultdict(list))
    team_transactions = defaultdict(lambda: {'Added': [], 'Dropped': []})

    # Process each transaction
    for transaction in waiver_activity:

       # Create a timezone-unaware datetime object from the timestamp
        try:
            transaction_time = datetime.fromtimestamp(transaction.timestamp)
        except:
            continue
        # Set the timezone to UTC
        transaction_time = transaction_time.replace(tzinfo=timezone.utc)        
        if transaction_time >= twenty_four_hours_ago and transaction.type == "add/drop":
            for player in transaction.players:
                player_data = player.transaction_data
                team_key = player_data.destination_team_key if player_data.type == "add" else player_data.source_team_key
                action = "Added" if player_data.type == "add" else "Dropped"
                player_info = f"{player.name.full} | ({player.editorial_team_abbr} - {player.display_position})"
                if player_data.type == "add" and player_data.source_type == "waivers":
                    player_info += " [W]"
                if transaction.faab_bid is not None:
                    player_info += f" | (${transaction.faab_bid})"
                team_transactions[team_key][action].append(player_info)

    # Format the transactions for each team
    for team_key, actions in team_transactions.items():
        if team_key in teams_info:
            moves_made = teams_info[team_key]
            team_info = f"{team_names.get(team_key, 'Unknown Team')} (#{moves_made})"
            formatted_activity += f"{team_info}\n"
            for action, players in actions.items():
                formatted_activity += "\n".join([f"{action} {player}" for player in players]) + "\n"
        formatted_activity += "\n"

    if team_transactions:
        aligned = formatted_activity.split('\n')
        msg = align_messages(aligned) 
        msg = "Transaction Report For Last 24 Hours:\n\n" + msg
    return msg if team_transactions else ""

def get_auth_dir():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, "auth")

def get_current_week(qry):
    return qry.get_league_info().current_week


def align_messages(messages):
    split_lines = [line.split(" | ") for line in messages if line.strip()]

    # Calculate maximum length of each section and the overall max length
    max_sections = max(len(line) for line in split_lines)
    max_lengths = [0] * max_sections
    overall_max_length = 0
    for line in split_lines:
        for i, section in enumerate(line):
            max_lengths[i] = max(max_lengths[i], len(section.strip()))
        overall_max_length = max(overall_max_length, sum(max_lengths) + (len(line) - 1) * 3)  # 3 = len(" | ")

    # Construct aligned lines
    aligned_lines = []
    for line in split_lines:
        if len(line) == 1 and "|" not in line[0]:  # Center align if no |
            aligned_lines.append("")  # Add an additional newline
            aligned_lines.append(line[0].center(overall_max_length))
            aligned_lines.append("")  # Add an additional newline
        else:
            aligned_line = []
            for i, section in enumerate(line):
                # Left align for all sections except the last section in the longest lines
                if i < len(line) - 1 or len(line) < max_sections:
                    aligned_line.append(section.ljust(max_lengths[i]))
                else:
                    aligned_line.append(section.rjust(max_lengths[i]))

            aligned_lines.append(" | ".join(aligned_line))

    return '\n'.join(aligned_lines)