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


