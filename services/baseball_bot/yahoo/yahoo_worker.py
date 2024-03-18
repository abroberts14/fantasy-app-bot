from yfpy.query import YahooFantasySportsQuery
from datetime import datetime, timedelta, timezone
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import os
import logging
from dotenv import load_dotenv
import random
import itertools 

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

def yf_get_hypothetical_records(qry):
    current_week = get_current_week(qry)
    league_matchups = qry.get_league_scoreboard_by_week(current_week).matchups
    all_teams = [team for matchup in league_matchups for team in matchup.teams if len(matchup.teams) == 2]

    # Initialize records
    records = {team.name.decode('utf-8'): {'wins': 0, 'losses': 0, 'ties': 0} for team in all_teams}

    # Compare each team against all others
    for team1, team2 in itertools.combinations(all_teams, 2):
        team1_score = team1.team_points.total
        team2_score = team2.team_points.total
        team1_name = team1.name.decode('utf-8')
        team2_name = team2.name.decode('utf-8')

        if team1_score > team2_score:
            records[team1_name]['wins'] += 1
            records[team2_name]['losses'] += 1
        elif team1_score < team2_score:
            records[team1_name]['losses'] += 1
            records[team2_name]['wins'] += 1
        else:
            records[team1_name]['ties'] += 1
            records[team2_name]['ties'] += 1

    # Format the output
    formatted_records = "Hypothetical League Records:\n\n"
    for team_name, record in records.items():
        formatted_records += f"{team_name}: {record['wins']}-{record['losses']}-{record['ties']}\n"

    return formatted_records.strip()

def yf_get_league_matchups(qry):
    current_week = get_current_week(qry)
    league_matchups = qry.get_league_scoreboard_by_week(current_week).matchups
     # Emoji assignments
    highest_score_emoji = "🏆"
    lowest_score_emoji = "🤡"
    default_emoji = "🔹"
    first_place_emoji = "🥇"
    second_place_emoji = "🥈"
    blowout_emoji = "💣"
    alert_emoji = "🚨"

    formatted_matchups = f" {highest_score_emoji} League Scores: {highest_score_emoji} \n\n"
    mock_data = False
    mocked_scores = {}
    # Find highest and lowest scores and biggest blowout
   # all_scores = [team.team_points.total for matchup in league_matchups for team in matchup.teams if len(matchup.teams) == 2]
    all_scores = []

    blowout_difference = 0
    blowout_matchup = None



    for matchup in league_matchups:
        teams = matchup.teams
        if len(teams) == 2:  # Ensure there are two teams in the matchup
            team_1_score = teams[0].team_points.total
            team_2_score = teams[1].team_points.total

            if mock_data:
                team_1_score = int(round(random.uniform(0, 14), 1))
                team_2_score = int(round(random.uniform(0, 14 - team_1_score), 1))

                team_1_score = max(team_1_score, 1 - team_2_score)

                # Store mocked scores
                mocked_scores[teams[0].name] = team_1_score
                mocked_scores[teams[1].name] = team_2_score
            all_scores.extend([team_1_score, team_2_score])

            # Determine blowout
            score_difference = abs(team_1_score - team_2_score)
            if score_difference > blowout_difference:
                blowout_difference = score_difference
                blowout_matchup = matchup
            
    highest_score = max(all_scores)
    lowest_score = min(all_scores)
    # Use default emoji if all scores are 0
    if highest_score == 0:
        emoji_for_all = default_emoji
    else:
        emoji_for_all = None
    for matchup in league_matchups:
        teams = matchup.teams

        if len(teams) == 2:
            team_1 = teams[0]
            team_2 = teams[1]
            team_1_name = team_1.name.decode('utf-8')
            team_1_score = int(team_1.team_points.total)
            team_2_name = team_2.name.decode('utf-8')
            team_2_score = int(team_2.team_points.total)

            if mock_data:
                # Retrieve mocked scores
                team_1_score = mocked_scores[team_1.name]
                team_2_score = mocked_scores[team_2.name]

            is_blowout = matchup == blowout_matchup

            if emoji_for_all:
                team_1_emoji = team_2_emoji = emoji_for_all
            else:
                team_1_emoji = highest_score_emoji if team_1_score == highest_score else lowest_score_emoji if team_1_score == 0 else first_place_emoji if team_1_score > team_2_score else second_place_emoji
                team_2_emoji = highest_score_emoji if team_2_score == highest_score else lowest_score_emoji if team_2_score == 0 else first_place_emoji if team_2_score > team_1_score else second_place_emoji

            matchup_line = f"{team_1_emoji} {team_1_name} - {team_1_score}\n{team_2_emoji} {team_2_name} - {team_2_score}"
            formatted_matchups += f"{alert_emoji} {alert_emoji} LARGEST LEAD {alert_emoji} {alert_emoji} \n{matchup_line} \n\n" if is_blowout else f"{matchup_line}\n\n"

    return formatted_matchups.strip()

def get_league_standings(qry):
    standings = qry.get_league_standings().teams
    week = get_current_week(qry)
    standings_str = f"🏆 League Standings - Week {week} 🏆\n\n"
    last_place = len(standings)  # Assuming 'standings' is a list

    for team in standings:
        print(team.team_standings)
        rank = team.team_standings.rank
        name = team.name.decode('utf-8')
        wins = team.team_standings.outcome_totals.wins
        losses = team.team_standings.outcome_totals.losses
        ties = team.team_standings.outcome_totals.ties
        if rank == None:
            rank = 0
        # Adding emoji based on rank
        if rank == 1:
            rank_str = "🥇"
        elif rank == 2:
            rank_str = "🥈"
        elif rank == last_place:
            rank_str = "🤡"
        else:
            rank_str = f"{rank}"

        standings_str += f"{rank_str}: {name} - {wins}-{losses}-{ties}\n"

    return standings_str

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


    p_add = "➕"
    p_drop = "➖"
    # Initialize a defaultdict for storing transactions
    #team_transactions = defaultdict(lambda: defaultdict(list))
    team_transactions = defaultdict(lambda: {p_add: [], p_drop: []})

    # Process each transaction
    for transaction in waiver_activity:

       # Create a timezone-unaware datetime object from the timestamp
        try:
            transaction_time = datetime.fromtimestamp(transaction.timestamp)
        except:
            continue
        # Set the timezone to UTC
        transaction_time = transaction_time.replace(tzinfo=timezone.utc)        
        if transaction_time >= twenty_four_hours_ago and (transaction.type == "add/drop" or transaction.type == "add" or transaction.type == "drop"):
            for player in transaction.players:
                player_data = player.transaction_data
                team_key = player_data.destination_team_key if player_data.type == "add" else player_data.source_team_key
                action = p_add if player_data.type == "add" else  p_drop
                player_info = f"{player.name.full}  ({player.editorial_team_abbr} - {player.display_position})"
                if player_data.type == "add" and player_data.source_type == "waivers":
                    player_info += " [W]"
                if transaction.faab_bid is not None:
                    player_info += f" | (${transaction.faab_bid})"
                team_transactions[team_key][action].append(player_info)

    # Format the transactions for each team
    for team_key, actions in team_transactions.items():
        if team_key in teams_info:
            moves_made = teams_info[team_key]
            team_info = f"\n🔹 {team_names.get(team_key, 'Unknown Team')}🔹 (#{moves_made})"
            formatted_activity += f"{team_info}\n"
            for action, players in actions.items():
                formatted_activity += "\n".join([f"{action} {player}" for player in players]) + "\n"
        #formatted_activity += "\n"

    if team_transactions:
        #aligned = formatted_activity.split('\n')
        #msg = align_messages(aligned) 
        msg = "Transaction Report For Last 24 Hours:\n" + formatted_activity
    return msg if team_transactions else ""

def trade_tracker(qry):
    transactions = qry.get_league_transactions()
    teams = qry.get_league_teams()
    teams_info, team_names = get_teams_info(teams)
    ten_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=11)

    trade_alert = ''
    trades = defaultdict(lambda: {'trader_players': [], 'tradee_players': []})

    for transaction in transactions:
        try:
            transaction_time = datetime.fromtimestamp(transaction.timestamp).replace(tzinfo=timezone.utc)
        except:
            continue

        if transaction_time >= ten_minutes_ago and transaction.type == "trade":
            # Collecting player info for the transaction
            for player in transaction.players:
                player_info = f"🔹 {player.name.full} ({player.editorial_team_abbr} - {player.display_position})"
                if player.transaction_data.destination_team_key == transaction.trader_team_key:
                    trades[(transaction.trader_team_key, transaction.tradee_team_key, transaction_time.timestamp())]['trader_players'].append(player_info)
                else:
                    trades[(transaction.trader_team_key, transaction.tradee_team_key, transaction_time.timestamp())]['tradee_players'].append(player_info)

    for (trader_key, tradee_key, timestamp), players in trades.items():
        trader_name = team_names.get(trader_key, 'Unknown Team')
        tradee_name = team_names.get(tradee_key, 'Unknown Team')
        trade_time = datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y, %H:%M:%S")

        trade_alert += f"🚨 Trade Alert! 🚨\n{trader_name} traded with {tradee_name}\n\n"
        trade_alert += f"{trader_name} received:\n" + '\n'.join(players['trader_players']) + "\n\n"
        trade_alert += f"{tradee_name} received:\n" + '\n'.join(players['tradee_players']) + "\n\n"

    return trade_alert if trades else ""


def get_starter_count(qry):
    sc =  yf_get_starter_counts(qry)
    logging.info(f"Starter Count: {sc}")
    return sc
def get_current_team_players(qry):
    team = yf_get_current_user_team(qry)
    if team is None:
        return "⚠️ No team found for the current login."
    return yf_get_team_players(qry, team)


def yf_get_team_players(query, team, formatted = True):
    try:
        # Using yfpy_query to get the players for the given team
        players = query.get_team_roster_by_week(team.team_id, get_current_week(query))
        if not players:
            return "⚠️ No players found for this team."

        players_list = []
        on_pitchers = False 
        players_list.append("🔹 Batters 🔹") 

        for player in players.players:
            print(player)
            first_letter = player.name.first[0]
            display_name = f"{first_letter}. {player.name.last}"

            if "P" in player.display_position and not on_pitchers:
                on_pitchers = True
                players_list.append("🔹 Pitchers 🔹") 
            player_info = f" {player.selected_position.position}: {display_name} {player.editorial_team_abbr} - {player.display_position}"
            print(player)
            players_list.append(player_info)

        formatted_response = f"🏅 {team.name.decode('utf-8')  } Roster:\n" + "\n".join(players_list)
        if formatted:
            return formatted_response
        else:
            return players.players

    except Exception as e:
        return f"❗ An error occurred: {e}"

def yf_get_current_user_team(query):
    try:
        teams = query.get_league_teams()

        for team in teams:
            if team.is_owned_by_current_login:
                return team

        return None  # No team is owned by the current login

    except Exception as e:
        return f"❗ An error occurred: {e}"
    


def yf_get_starter_counts(query):
    """
    Get the number of starters for each position

    Parameters
    ----------
    league : object
        The league object for which the starter counts are being generated

    Returns
    -------
    dict
        A dictionary containing the number of players at each position within the starting lineup.
    """

    # Get the box scores for last week
    last_week = get_current_week(query) #subtract by 1 when data is available
    #box_scores = league.box_scores(week=league.current_week - 1)
    mathcups = query.get_league_scoreboard_by_week(last_week).matchups

    # Initialize a dictionary to store the home team's starters and their positions
    h_starters = {}
    # Initialize a variable to keep track of the number of home team starters
    h_starter_count = 0
    # Initialize a dictionary to store the away team's starters and their positions
    a_starters = {}
    # Initialize a variable to keep track of the number of away team starters
    a_starter_count = 0
    
    
    for matchup in mathcups:
        teams = matchup.teams

        if len(teams) == 2:  # Ensure there are two teams in the matchup
            home_team = teams[1]
            home_team_roster = query.get_team_roster_by_week(home_team.team_id, last_week)
            for player in home_team_roster.players:
                # Check if the player is a starter (not on the bench or injured)
                if (player.selected_position.position != 'BN' and player.selected_position.position != 'IL'):
                    # Increment the number of home team starters
                    h_starter_count += 1
                    try:
                        # Try to increment the count for this position in the h_starters dictionary
                        h_starters[player.selected_position.position] = h_starters[player.selected_position.position] + 1
                    except KeyError:
                        # If the position is not in the dictionary yet, add it and set the count to 1
                        h_starters[player.selected_position.position] = 1
            away_team = teams[0]
            away_team_roster = query.get_team_roster_by_week(away_team.team_id, last_week)
            for player in away_team_roster.players:
                # Check if the player is a starter (not on the bench or injured)
                if (player.selected_position.position != 'BE' and player.selected_position.position != 'IL'):
                    # Increment the number of home team starters
                    a_starter_count += 1
                    try:
                        # Try to increment the count for this position in the h_starters dictionary
                        a_starters[player.selected_position.position] = a_starters[player.selected_position.position] + 1
                    except KeyError:
                        # If the position is not in the dictionary yet, add it and set the count to 1
                        a_starters[player.selected_position.position] = 1


            # if statement for the ultra rare case of a matchup with both entire teams (or one with a bye) on the bench
            if a_starter_count!=0 and h_starter_count != 0:
                if a_starter_count > h_starter_count:
                    return a_starters
                else:
                    return h_starters

  
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