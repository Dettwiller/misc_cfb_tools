import os
import pandas as pd
from datetime import datetime
from . import fetch_data

class Team:
    name = ''
    data_dir = os.path.join(os.getcwd(), 'data')
    raw_game_data = None
    game_data = None
    drive_data = None
    def __init__(self, name, data_dir=None):
        '''
            TODO: input checking:
                1. name is a string
                    a. have an excel file of all team names and check that it exists
                2. if data_dir is not None, add logic to ensure data_dir:
                    a. is a path
                    b. exists
                    c. create the passed data_dir if it doesn't exist
        '''
        self.name = name
        if data_dir is not None:
            self.data_dir = data_dir

    def get_drive_data(self, timeline=[datetime.now().year - 4, datetime.now().year - 1]):
        if self.drive_data:
            return self.drive_data
        else:
            self.drive_data = fetch_data.get_game_data(self.name, data='drives', timeline=timeline, data_dir=self.data_dir)
            return self.drive_data

    def get_game_data(self, timeline=[1880, datetime.now().year - 1]):
        if self.game_data:
            return self.game_data
        else:
            self.raw_game_data = fetch_data.get_game_data(self.name, data='games', timeline=timeline, data_dir=self.data_dir)
            self.__process_game_data()
            return self.game_data

    def __process_game_data(self):
        away_games = self.raw_game_data.index[self.raw_game_data['away_team'] == self.name]
        home_games = self.raw_game_data.index[self.raw_game_data['home_team'] == self.name]
        games_list = away_games.tolist() + home_games.tolist()
        games_list.sort()

        games = pd.Index(games_list)
        games_df = self.raw_game_data.loc[games]

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
        self.game_data = pd.DataFrame(data={'seasons': seasons, 'points_scored': points_scored, 
                                        'points_allowed': points_allowed, 'point_diff': point_diff, 'result': result})


        


