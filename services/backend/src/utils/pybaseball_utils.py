import io
import os
from datetime import datetime, timedelta
from typing import List, Optional, Union

import pandas as pd
import requests
from pybaseball.datahelpers.column_mapper import (
    BattingStatsColumnMapper,
    ColumnListMapperFunction,
)
from pybaseball.datasources.fangraphs import FangraphsDataTable, player_row_id_func
from pybaseball.datasources.html_table_processor import RowIdFunction
from pybaseball.enums.fangraphs import (
    FangraphsBattingStats,
    FangraphsLeague,
    FangraphsPositions,
    FangraphsStatColumn,
    FangraphsStatsCategory,
    stat_list_from_str,
    stat_list_to_str,
)

_FG_LEADERS_URL = "/leaders-legacy.aspx"

MIN_AGE = 0
MAX_AGE = 100
# Extend the FangraphsMonth enum with additional attributes

from pybaseball.enums.enum_base import EnumBase


class FangraphsMonthExtended(EnumBase):
    ALL = 0
    LAST_SEVEN = 1
    LAST_FOURTEEN = 2
    LAST_THIRTY = 3
    MARCH_APRIL = 4
    MARCH = MARCH_APRIL
    APRIL = MARCH_APRIL
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER_OCTOBER = 9
    SEPTEMBER = SEPTEMBER_OCTOBER
    OCTOBER = SEPTEMBER_OCTOBER


class ExtendedFangraphsDataTable(FangraphsDataTable):
    def __init__(self):
        super().__init__()

    def fetch_extended(
        self,
        start_season: int,
        end_season: Optional[int] = None,
        league: str = "ALL",
        ind: int = 1,
        stat_columns: Union[str, List[str]] = "ALL",
        qual: Optional[int] = None,
        split_seasons: bool = True,
        month: str = "ALL",
        on_active_roster: bool = False,
        minimum_age: int = 0,
        maximum_age: int = 100,
        team: str = "",
        _filter: str = "",
        players: str = "",
        position: str = "ALL",
        max_results: int = 1000000,
    ) -> pd.DataFrame:
        """
        Get extended leaderboard data from Fangraphs with additional month options.

        ARGUMENTS:
        start_season       : int              : First season to return data for
        end_season         : int              : Last season to return data for
                                                Default = start_season
        league             : str              : League to return data for: ALL, AL, FL, NL
                                                Default = ALL
        ind                : int              : DEPRECATED. ONLY FOR BACKWARDS COMPATIBILITY. USE split_seasons INSTEAD
                                                1 if you want individual season-level data
                                                0 if you want a player's aggreagate data over all seasons in the query
        stat_columns       : str or List[str] : The columns of data to return
                                                Default = ALL
        qual               : Optional[int]    : Minimum number of plate appearances to be included.
                                                If None is specified, the Fangraphs default ('y') is used.
                                                Default = None
        split_seasons      : bool             : True if you want individual season-level data
                                                False if you want aggregate data over all seasons.
                                                Default = False
        month              : str              : Month to filter data by. 'ALL' to not filter by month.
                                                Default = 'ALL'
        on_active_roster   : bool             : Only include active roster players.
                                                Default = False
        minimum_age        : int              : Minimum player age.
                                                Default = 0
        maximum_age        : int              : Maximum player age.
                                                Default = 100
        team               : str              : Team to filter data by.
                                                Specify "0,ts" to get aggregate team data.
        position           : str              : Position to filter data by.
                                                Default = ALL
        max_results        : int              : The maximum number of results to return.
                                                Default = 1000000 (In effect, all results)
        """
        print("EXTENDED fetch")
        stat_columns_enums = stat_list_from_str(self.STATS_CATEGORY, stat_columns)

        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. "
                + "Try specifying start_season or start_season and end_season."
            )

        if end_season is None:
            end_season = start_season

        assert self.STATS_CATEGORY is not None

        if league is None:
            raise ValueError("parameter 'league' cannot be None.")

        url_options = {
            "pos": FangraphsPositions.parse(position).value,
            "stats": self.STATS_CATEGORY.value,
            "lg": FangraphsLeague.parse(league.upper()).value,
            "qual": qual if qual is not None else "y",
            "type": stat_list_to_str(stat_columns_enums),
            "season": end_season,
            "month": FangraphsMonthExtended.parse(month).value,
            "season1": start_season,
            "ind": ind if ind == 0 and split_seasons else int(split_seasons),
            "team": f"{team or 0},ts" if self.TEAM_DATA else team,
            "rost": int(on_active_roster),
            "age": f"{minimum_age},{maximum_age}",
            "filter": _filter,
            "players": players,
            "page": f"1_{max_results}",
        }
        print("EXTENDED OBJECT")
        print(url_options)
        return self._validate(
            self._postprocess(
                self.html_accessor.get_tabular_data_from_options(
                    self.QUERY_ENDPOINT,
                    query_params=url_options,
                    # TODO: Remove the type: ignore after this is fixed: https://github.com/python/mypy/issues/5485
                    column_name_mapper=self.COLUMN_NAME_MAPPER,  # type: ignore
                    known_percentages=self.KNOWN_PERCENTAGES,
                    row_id_func=self.ROW_ID_FUNC,
                    row_id_name=self.ROW_ID_NAME,
                )
            )
        )


class ExtendedFangraphsBattingTable(ExtendedFangraphsDataTable):
    def __init__(self):
        super().__init__()

    STATS_CATEGORY: FangraphsStatsCategory = FangraphsStatsCategory.BATTING
    DEFAULT_STAT_COLUMNS: List[FangraphsStatColumn] = FangraphsBattingStats.ALL()
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = BattingStatsColumnMapper().map_list
    KNOWN_PERCENTAGES: List[str] = ["GB/FB"]
    ROW_ID_FUNC: RowIdFunction = player_row_id_func
    ROW_ID_NAME = "IDfg"

    def fetch(self, *args, **kwargs):
        return super().fetch(*args, **kwargs)

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        return self._sort(data, ["WAR", "OPS"], ascending=False)


fg_batting_data_extended = ExtendedFangraphsBattingTable().fetch_extended


# retrieve all players' batting stats for the month of May, 2017
def split_request(
    start_dt: str,
    end_dt: str,
    player_id: int,
    url: str,
) -> pd.DataFrame:
    """
    Splits Statcast queries to avoid request timeout
    """
    current_dt = datetime.strptime(start_dt, "%Y-%m-%d")
    end_dt_datetime = datetime.strptime(end_dt, "%Y-%m-%d")
    results = []  # list to hold data as it is returned
    player_id_str = str(player_id)
    print("Gathering Player Data")
    print(f"start_dt: {start_dt}, end_dt: {end_dt}, player_id: {player_id}")
    # break query into multiple requests
    while current_dt <= end_dt_datetime:
        remaining = end_dt_datetime - current_dt
        # increment date ranges by at most 60 days
        delta = min(remaining, timedelta(days=2190))
        next_dt = current_dt + delta
        start_str = current_dt.strftime("%Y-%m-%d")
        end_str = next_dt.strftime("%Y-%m-%d")
        # retrieve data
        print(f"url: {url.format(start_str, end_str, player_id_str)}")
        data = requests.get(url.format(start_str, end_str, player_id_str))
        df = pd.read_csv(io.StringIO(data.text))
        # add data to list and increment current dates
        results.append(df)
        current_dt = next_dt + timedelta(days=1)
    return pd.concat(results)


def get_register_file():
    # Get the directory of the current file
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # Join this directory with the filename
    return os.path.join(current_file_dir, "chadwick-register.csv")


def clean_data(player_table):
    """Cleans the player table by removing rows considered 'bad data'."""
    # Convert to string and ensure trimming
    player_table["name_first"] = player_table["name_first"].astype(str).str.strip()
    player_table["name_last"] = player_table["name_last"].astype(str).str.strip()

    # Remove rows with empty first or last names
    player_table = player_table[
        (player_table["name_first"] != "") & (player_table["name_last"] != "")
    ]

    # Additional checks can be added here, e.g., negative identifiers or implausible years
    return player_table


def find_player_fangraphs_id(player_id: int) -> pd.DataFrame:
    """Lookup playerIDs for a given player"""
    print(f"find_player_fangraphs_id: looking for {player_id}")
    table = pd.read_csv(get_register_file())
    table = clean_data(table)

    print("table columns", table.columns)
    results = table[table["key_mlbam"] == player_id]

    results = results.reset_index(drop=True)

    print("found ", len(results), " players")
    if len(results) > 0:
        if player_id == 701538:
            # print each key and value in the first row of the dataframe
            print(results.iloc[0])

        res = results.iloc[0]["key_fangraphs"]
        print(f"find_player_fangraphs_id: {res}")
    else:
        res = None
        print(f"find_player_fangraphs_id: no results found for {player_id}")
    # return the first items value at key_fangraphs
    return res


def custom_statcast_batter(
    start_dt: Optional[str] = None,
    end_dt: Optional[str] = None,
    player_id: Optional[int] = None,
) -> pd.DataFrame:
    """
    Pulls statcast pitch-level data from Baseball Savant for a given batter.

    ARGUMENTS
        start_dt : YYYY-MM-DD : the first date for which you want a player's statcast data
        end_dt : YYYY-MM-DD : the final date for which you want data
        player_id : INT : the player's MLBAM ID. Find this by calling pybaseball.playerid_lookup(last_name, first_name),
            finding the correct player, and selecting their key_mlbam.
    """

    new_url = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=batter&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={}&game_date_lt={}&batters_lookup%5B%5D={}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&chk_stats_sweetspot_speed_mph=on&chk_stats_swing_length=on&type=details&"
    print(
        f"fetching custom statcast batter for player {player_id} from {start_dt} to {end_dt}"
    )
    df = split_request(start_dt, end_dt, player_id, new_url)
    print(
        f"returning custom statcast batter for player {player_id} from {start_dt} to {end_dt}"
    )
    return df
