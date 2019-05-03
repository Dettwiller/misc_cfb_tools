import os
from . import fetch_data, utility
class Team:
    def __init__(self, name, data_dir=os.path.join(os.getcwd(), 'data')):
        self.name = name
        self.data_dir = data_dir
        #TODO: deprecate get_team_drive_data in favor of get_team_data for full dataframe
        self.drive_data = None
        self.hist_data = None
        self.recent_data = None
        self.current_data = None

    def calc_ppd_dists(self, timeline = [2016, 2018]):
        self.drive_data = fetch_data.get_team_drive_data(self.name, timeline=timeline, data_dir=self.data_dir)
        seasons = []
        for i in range(timeline[0], timeline[1] + 1):
            seasons += [i]
        self.hist_data = self.drive_data.loc[self.drive_data['season'].isin(seasons)]
        self.recent_data = self.drive_data.loc[self.drive_data['season'] == timeline[1]]
        self.current_data = utility.recent_games(self.drive_data, last_games=3)

        self.drive_dists = {}
        self.drive_dists['hist'] = utility.calculate_ppd(self.name, self.hist_data)
        self.drive_dists['recent'] = utility.calculate_ppd(self.name, self.recent_data)
        self.drive_dists['current'] = utility.calculate_ppd(self.name, self.current_data)

        # results_3_season = utility.calculate_ppd(self.name, self.season_3_data)
        # results_season = utility.calculate_ppd(self.name, self.season_data)
        # results_3_game = utility.calculate_ppd(self.name, self.game_3_data)

        # ppd_3s_offense_dist = du.discritize_distribution(results_3_season['offense'], results_3_season['offense_stddv'], res=10000)
        # ppd_3s_defense_dist = du.discritize_distribution(results_3_season['defense'], results_3_season['defense_stddv'], res=10000)
        # dpg_3s_dist = du.discritize_distribution(results_3_season['dpg'], results_3_season['dpg_stddv'], res=10000)

        # ppd_s_offense_dist = du.discritize_distribution(results_season['offense'], results_season['offense_stddv'], res=10000)
        # ppd_s_defense_dist = du.discritize_distribution(results_season['defense'], results_season['defense_stddv'], res=10000)
        # dpg_s_dist = du.discritize_distribution(results_season['dpg'], results_season['dpg_stddv'], res=10000)

        # ppd_3g_offense_dist = du.discritize_distribution(results_3_game['offense'], results_3_game['offense_stddv'], res=10000)
        # ppd_3g_defense_dist = du.discritize_distribution(results_3_game['defense'], results_3_game['defense_stddv'], res=10000)
        # dpg_3g_dist = du.discritize_distribution(results_3_game['dpg'], results_3_game['dpg_stddv'], res=10000)

        # self.drive_dists['offense_3s'] = ppd_3s_offense_dist
        # self.drive_dists['defense_3s'] = ppd_3s_defense_dist
        # self.drive_dists['dpg_3s'] = dpg_3s_dist

        # self.drive_dists['offense_s'] = ppd_s_offense_dist
        # self.drive_dists['defense_s'] = ppd_s_defense_dist
        # self.drive_dists['dpg_s'] = dpg_s_dist

        # self.drive_dists['offense_3g'] = ppd_3g_offense_dist
        # self.drive_dists['defense_3g'] = ppd_3g_defense_dist
        # self.drive_dists['dpg_3g'] = dpg_3g_dist

        


