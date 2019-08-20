from datetime import datetime
from os import getcwd

import pandas as pd

from football_modeling import fetch_data, tools


def team(name, data_dir=getcwd(), games_dir=getcwd(), drives_dir=getcwd()):
# def team(name, data_dir=getcwd()):
    team_ = Team(name, data_dir=data_dir, games_dir=games_dir, drives_dir=drives_dir)
    # team_ = Team(name, data_dir=data_dir)
    return team_

class Team:
    def __init__(self, name, data_dir=getcwd(), games_dir=getcwd(), drives_dir=getcwd()):
    # def __init__(self, name, data_dir=getcwd()):
        name_type_check = isinstance(name, str)
        assert name_type_check, "name is not a string: %r" % type(name)
        tools.directory_check(data_dir)
        tools.directory_check(games_dir)
        tools.directory_check(drives_dir)

        self.name = name
        self.data_dir = data_dir
        self.games_dir = games_dir
        self.drives_dir = drives_dir
        self.data_downloader = fetch_data.data_downloader(data_dir=self.data_dir)
        self.drive_data = pd.DataFrame()
        self.game_data = pd.DataFrame()

    def __process_game_data(self, raw_game_data):
        away_games = raw_game_data.index[raw_game_data['away_team'] == self.name]
        home_games = raw_game_data.index[raw_game_data['home_team'] == self.name]
        games_list = away_games.tolist() + home_games.tolist()
        games_list.sort()

        games = pd.Index(games_list)
        games_df = raw_game_data.loc[games]

        points_scored = []
        points_allowed = []
        point_diff = []
        result = []
        seasons = []
        for row in games_df.itertuples(name='game'):
            if row.away_team == self.name:
                points_scored += [row.away_points]
                points_allowed +=[row.home_points]
                point_diff += [row.away_points - row.home_points]
            else:
                points_scored += [row.home_points]
                points_allowed +=[row.away_points]
                point_diff += [row.home_points - row.away_points]
            if point_diff[-1] > 0:
                result += [1]
            else:
                result += [0]
            seasons += [row.season]
        game_data = pd.DataFrame(data={'season': seasons, 'points_scored': points_scored,
                                        'points_allowed': points_allowed,
                                        'point_diff': point_diff, 'result': result})
        return game_data

    def get_data(self, timeline, data_type='games', print_progress=False):
        tools.timeline_check(timeline)
        data_types_type_check = isinstance(data_type, str)
        assert data_types_type_check, "data_type is not string: %r" % type(data_type)
        data_types_value_check = data_type in self.data_downloader.acceptable_data_types
        assert data_types_value_check, "data_type (" + data_type + ") must be one of: %r" % self.data_downloader.acceptable_data_types
        print_progress_type_check = isinstance(print_progress, bool)
        assert print_progress_type_check, "print_progress is not bool: %r" % type(print_progress)

        if data_type == 'games' and not self.game_data.empty:
            self.data_downloader.change_download_directory(self.games_dir)
            if print_progress: print("returning existing game_data")
            return_data =  self.game_data
        elif data_type == 'games' and self.game_data.empty:
            if print_progress: print("downloading game_data")
            self.data_downloader.change_download_directory(self.games_dir)
            raw_game_data = self.data_downloader.get_data(teams=[self.name], data_type='games', timeline=timeline, print_progress=print_progress)
            self.game_data = self.__process_game_data(raw_game_data[self.name])
            return_data =  self.game_data
        elif data_type == 'drives' and not self.drive_data.empty:
            self.data_downloader.change_download_directory(self.drives_dir)
            if print_progress: print("returning existing drive_data")
            return_data = self.drive_data
        elif data_type == 'drives' and self.drive_data.empty:
            self.data_downloader.change_download_directory(self.drives_dir)
            requested_data = self.data_downloader.get_data(teams=[self.name], data_type='drives', timeline=timeline, print_progress=print_progress)
            self.drive_data = requested_data[self.name]
            return_data = self.drive_data
        return return_data
