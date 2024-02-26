from yfpy.query import YahooFantasySportsQuery

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
    current_week = get_current_week(qry)
    league_matchups = qry.get_league_scoreboard_by_week(current_week).matchups
    formatted_matchups = ''

    for matchup in league_matchups:
        teams = matchup.teams

        if len(teams) == 2:  # Ensure there are two teams in the matchup
            team_1 = teams[0]
            team_2 = teams[1]

            # Extract team names and scores, decode byte strings if necessary
            team_1_name = team_1.name.decode('utf-8') if isinstance(team_1.name, bytes) else team_1.name
            team_1_score =  int(team_1.team_points.total)
            team_2_name = team_2.name.decode('utf-8') if isinstance(team_2.name, bytes) else team_2.name
            team_2_score = int(team_2.team_points.total)

            formatted_matchups += f"{team_1_name} Vs {team_2_name}\n{team_1_score} - {team_2_score}\n\n"

    return formatted_matchups

def get_current_week(qry):
    return qry.get_league_info().current_week