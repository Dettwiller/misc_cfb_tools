import os
import numpy as np
from scipy.stats import norm
from . import fetch_data
from . import utility
class Team:
    def __init__(self, name, timeline = [2016, 2018], data_dir=os.getcwd()):
        self.name = name
        #TODO: deprecate get_team_drive_data in favor of get_team_data for full dataframe
        #TODO: axis='season' is not valid, should be column, but that doesn't do what we want
        self.all_data = fetch_data.get_team_drive_data(name, timeline=timeline, data_dir=data_dir)
        self.season_3_data = self.all_data.filter(like=str(timeline[0]), axis='season')
        for i in range(timeline[0] + 2, timeline[1] + 1):
            year = str(i)
            new_df = self.all_data.filter(like=year, axis='season')
            self.season_3_data.append(new_df, ignore_index=True)
        self.season_data = self.all_data.filter(like=str(timeline[1]), axis='season')
        self.game_3_data = utility.recent_games(self.all_data, last_games=3)
        self.drive_dists = {}

    
    def calc_ppd_dist(self):
        results_3_season = utility.calculate_ppd(self.name, self.season_3_data)
        results_season = utility.calculate_ppd(self.name, self.season_data)
        results_3_game = utility.calculate_ppd(self.name, self.game_3_data)

        #ppd

        line_ppd_offense_3_season = [results_3_season['offense'] - 6 * results_3_season['offense_s'], results_3_season['offense'] + 6 * results_3_season['offense_s']]
        ppd_offense_3_season = np.linspace(line_ppd_offense_3_season[0], line_ppd_offense_3_season[1], 10000)
        line_ppd_defense_3_season = [results_3_season['defense'] - 6 * results_3_season['defense_s'], results_3_season['defense'] + 6 * results_3_season['defense_s']]
        ppd_defense_3_season = np.linspace(line_ppd_defense_3_season[0], line_ppd_defense_3_season[1], 10000)

        line_ppd_offense_season = [results_season['offense'] - 6 * results_season['offense_s'], results_season['offense'] + 6 * results_season['offense_s']]
        ppd_offense_season = np.linspace(line_ppd_offense_season[0], line_ppd_offense_season[1], 10000)
        line_ppd_defense_season = [results_season['defense'] - 6 * results_season['defense_s'], results_season['defense'] + 6 * results_season['defense_s']]
        ppd_defense_season = np.linspace(line_ppd_defense_season[0], line_ppd_defense_season[1], 10000)

        line_ppd_offense_3_game = [results_3_game['offense'] - 6 * results_3_game['offense_s'], results_3_game['offense'] + 6 * results_3_game['offense_s']]
        ppd_offense_3_game = np.linspace(line_ppd_offense_3_game[0], line_ppd_offense_3_game[1], 10000)
        line_ppd_defense_3_game = [results_3_game['defense'] - 6 * results_3_game['defense_s'], results_3_game['defense'] + 6 * results_3_game['defense_s']]
        ppd_defense_3_game = np.linspace(line_ppd_defense_3_game[0], line_ppd_defense_3_game[1], 10000)

        #dpg

        line_dpg_offense_3_season = [results_3_season['offense'] - 6 * results_3_season['offense_s'], results_3_season['offense'] + 6 * results_3_season['offense_s']]
        dpg_offense_3_season = np.linspace(line_dpg_offense_3_season[0], line_dpg_offense_3_season[1], 10000)
        line_dpg_defense_3_season = [results_3_season['defense'] - 6 * results_3_season['defense_s'], results_3_season['defense'] + 6 * results_3_season['defense_s']]
        dpg_defense_3_season = np.linspace(line_dpg_defense_3_season[0], line_dpg_defense_3_season[1], 10000)

        line_dpg_offense_season = [results_season['offense'] - 6 * results_season['offense_s'], results_season['offense'] + 6 * results_season['offense_s']]
        dpg_offense_season = np.linspace(line_dpg_offense_season[0], line_dpg_offense_season[1], 10000)
        line_dpg_defense_season = [results_season['defense'] - 6 * results_season['defense_s'], results_season['defense'] + 6 * results_season['defense_s']]
        dpg_defense_season = np.linspace(line_dpg_defense_season[0], line_dpg_defense_season[1], 10000)

        line_dpg_offense_3_game = [results_3_game['offense'] - 6 * results_3_game['offense_s'], results_3_game['offense'] + 6 * results_3_game['offense_s']]
        dpg_offense_3_game = np.linspace(line_dpg_offense_3_game[0], line_dpg_offense_3_game[1], 10000)
        line_dpg_defense_3_game = [results_3_game['defense'] - 6 * results_3_game['defense_s'], results_3_game['defense'] + 6 * results_3_game['defense_s']]
        dpg_defense_3_game = np.linspace(line_dpg_defense_3_game[0], line_dpg_defense_3_game[1], 10000)

        self.drive_dists['oppd_3s'] = ppd_offense_3_season
        self.drive_dists['dppd_3s'] = ppd_defense_3_season
        self.drive_dists['oppd_s'] = ppd_offense_season
        self.drive_dists['dppd_s'] = ppd_defense_season
        self.drive_dists['oppd_3g'] = ppd_offense_3_game
        self.drive_dists['dppd_3g'] = ppd_defense_3_game

        self.drive_dists['odpg_3s'] = dpg_offense_3_season
        self.drive_dists['ddpg_3s'] = dpg_defense_3_season
        self.drive_dists['odpg_s'] = dpg_offense_season
        self.drive_dists['ddpg_s'] = dpg_defense_season
        self.drive_dists['odpg_3g'] = dpg_offense_3_game
        self.drive_dists['ddpg_3g'] = dpg_defense_3_game

        


