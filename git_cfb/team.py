import os
import numpy as np
from . import fetch_data
from . import utility
class Team:
    def __init__(self, name, data_dir=os.getcwd()):
        self.name = name
        #TODO: deprecate get_team_drive_data in favor of get_team_data for full dataframe
        self.data = fetch_data.get_team_drive_data(name, data_dir=data_dir)

        self.ppd = {}

    def calculate_ppd(self):
        #TODO: add logic (may require refactor) to get ppd over seasons, season, and games
        #TODO: add logic to figure out if a game ended or quarter changed for turnover calcs
        #TODO: add game end/quarter logic for drives per game calculations
        turn_over = False
        offense_results = []
        defense_results = []
        for drive in self.data.itertuples(index=True, name='Drive'):
            drive_points, on_offense = utility.ppd_calculation(self.name, drive, turn_over=turn_over)
            if type(drive_points) == str:
                turn_over = True

            elif on_offense and not turn_over:
                offense_results += [drive_points]
                turn_over = False

            elif not on_offense and not turn_over:
                defense_results += [drive_points]
                turn_over = False

            elif not on_offense and turn_over:
                offense_results += [-1 * drive_points]
                defense_results += [drive_points]
                turn_over = False

            elif on_offense and turn_over:
                defense_results += [-1 * drive_points]
                offense_results += [drive_points]
                turn_over = False

        np_offense_results = np.array(offense_results)
        np_defense_results = np.array(defense_results)

        self.ppd['offense'] = np.mean(np_offense_results)
        self.ppd['offense_s'] = np.std(np_offense_results)
        self.ppd['defense'] = np.mean(np_defense_results)
        self.ppd['defense_s'] = np.std(np_defense_results)
        # ! THIS IS INCORRECT BELOW
        # TODO: calculate drives per game for the offense and defense
        # TODO: this is going to require logic for when a game ends
        # self.ppd['offense_dpg'] = len(np_offense_results)
        # self.ppd['offense_dpg_s'] = len(np_offense_results)
        # self.ppd['defense_dpg'] = len(np_defense_results)
        # self.ppd['defense_dpg_s'] = len(np_defense_results)
