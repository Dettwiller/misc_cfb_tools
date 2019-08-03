from datetime import datetime

import numpy as np
from scipy.stats import norm

from . import utility
from . import team


'''
    TODO: :
        1. 
'''

'''
    TODO: refactoring:
        1. no private functions should have var=var arguments
            defaults handled by outward facing functions
'''

class Model:
    home_team = ""
    away_team = ""
    neutral_site = False
    dist_home_team_score = None
    dist_away_team_score = None
    total = None
    diff = None

    def __init__(self, home_field = 0.0, neutral_site=False):
        # Type and value checking for unique inputs
        if isinstance(home_field, int):
            home_field = float(home_field)
        if not isinstance(home_field, float):
            raise TypeError("home_field should be a float but is " + str(type(home_field)))
        elif home_field < 0.0:
            raise ValueError("home_field should be >= 0.0 but is " + str(home_field))
        if not isinstance(neutral_site, bool):
            raise TypeError("neutral_site should be a bool but is " + str(type(neutral_site)))

        # Instance initializations and definitions
        if neutral_site:
            self.home_field = 0.0
        else:
            self.home_field = home_field

        # Instance initializations
        self.home_team = ""
        self.away_team = ""
        self.neutral_site = neutral_site
        self.dist_away_team_score = None
        self.dist_home_team_score = None
        self.total = None
        self.diff = None


class PPD_Model(Model):
    weights =  [0.15, 0.35, 0.5]
    def __init__(self, weights=[], home_field=None, neutral_site=False):
        # Type and value checking for unique inputs
        if not (isinstance(weights, list) or isinstance(weights, np.ndarray)):
            raise TypeError("weights must be a list or numpy array but is " + str(type(weights)))
        weights_sum = 0.0
        for i in range(len(weights)):
            if isinstance(weights[i], int):
                weights[i] = float(weights[i])
            if not isinstance(weights[i], float):
                raise TypeError("all members of weights must be floats but weights[" + str(i) + "] type is " + str(type(weights[i])))
            elif weights[i] < 0.0:
                raise ValueError("all members of weights must be >= 0.0 but weights[" + str(i) + "] is " + str(weights[i]))
            weights_sum += weights[i]
        if weights_sum != 1.0:
            raise ValueError("weights should sum to 1.0, but sum to " + str(weights_sum))

        # Instance initializations and definitions
        # lean on Model to do checking on home_field and neutral_site
        Model.__init__(self, home_field=home_field, neutral_site=neutral_site)
        if weights:
            self.weights = weights
        else:
            self.weights = [0.15, 0.35, 0.5]

    def __predict_score(self, home_team_dists, away_team_dists):
        # * Rules for normal distributions
        # * N(m1, v1) + N(m2, v2) = N(m1 + m2, v1 + v2)
        # * N(m1, v1) - N(m2, v2) = N(m1 - m2, v1 - v2)
        # * a*N(m1, v1) = N( a*m1, (a^2)*v1 ) 


        home_team_ppd = ( (home_team_dists['offense'][0] + away_team_dists['defense'][0]) / 2.0, 
                                (home_team_dists['offense'][1] + away_team_dists['defense'][1]) / 4.0 )
        
        away_team_ppd = ( (away_team_dists['offense'][0] + home_team_dists['defense'][0]) / 2.0, 
                                (away_team_dists['offense'][1] + home_team_dists['defense'][1]) / 4.0 )

        dpg = ( (home_team_dists['dpg'][0] + away_team_dists['dpg'][0]) / 2.0, 
                                (home_team_dists['dpg'][1] + away_team_dists['dpg'][1]) / 4.0 )

        # * May not always be self.home_team_score, could be components
        home_team_score = utility.dist_sample_mult(home_team_ppd, dpg, ns=100000)
        away_team_score = utility.dist_sample_mult(away_team_ppd, dpg, ns=100000)
        return home_team_score, away_team_score

    def __ppd_dists(self, team_name, drive_data, timeline, predicted_game=None):
        # TODO: with the new logic here deciding season spans, what is timeline?
        # TODO: how should timeline be used?
        # TODO: check to make sure timeline covers the spans considered?
        seasons = []
        for i in range(timeline[0], timeline[1] + 1):
            seasons += [i]
        # timeline = [2008, 2018]
        if predicted_game:
            if predicted_game in drive_data["game_id"].values:
                pg_first_drive_index =  drive_data[drive_data['game_id'] == predicted_game].index[0]
            else:
                previous_game = 0
                for game_id in drive_data["game_id"].values:
                    if int(game_id) > previous_game and int(game_id) < predicted_game:
                        previous_game = int(game_id)
                pg_first_drive_index = drive_data[drive_data['game_id'] == previous_game].index[0]
            # pg_first_drive_index = drive_data[drive_data['game_id'] == predicted_game].index[0]
            current_season = int(drive_data["season"].iloc[pg_first_drive_index])
        else:
            current_season = seasons[-1]
        hist_span = 5 # number of year's back to include in history
        recent_seasons = [current_season - i for i in range(1, 1 + hist_span)]
        hist_data = drive_data.loc[drive_data['season'].isin(recent_seasons)]
        recent_data = drive_data.loc[drive_data['season'] == current_season]
        if recent_data.empty:
            current_season -= 1
            recent_data = drive_data.loc[drive_data['season'] == current_season]            
        current_data = utility.drives_from_recent_games(drive_data, last_games=3, predicted_game=predicted_game)

        drive_dists = {}
        drive_dists['hist'] = self.__calculate_ppd(team_name, hist_data)
        drive_dists['recent'] = self.__calculate_ppd(team_name, recent_data)
        drive_dists['current'] = self.__calculate_ppd(team_name, current_data)
        return drive_dists

    def __drive_scoring(self, team_name, drive_tuple, turn_over=False):
        '''
            TODO: everything:
                1. this code has not been examined for improvement
        '''
        '''
            Consider asking for the next drives results for any change of 
            possession event, not just INT and FUMBLE
        '''
        drive_result = getattr(drive_tuple, "drive_result")
        if drive_result == "TD":
            return 7, getattr(drive_tuple, "offense") == team_name
        elif drive_result == "FG":
            return 3, getattr(drive_tuple, "offense") == team_name
        elif drive_result == "PUNT" or drive_result == "DOWNS" or turn_over:
            return 0, getattr(drive_tuple, "offense") == team_name
        else:
            return drive_result, getattr(drive_tuple, "offense") == team_name

    def __calculate_ppd(self, name, drives_df):
        '''
            TODO: everything:
                1. this code has not been examined for improvement
        '''
        #TODO: add logic to figure out if a game ended or quarter changed for turnover calcs
        turn_over = False
        offense_results = []
        defense_results = []
        drives_per_game = []
        game_drives = 0
        game = -1
        for drive in drives_df.itertuples(index=True, name='Drive'):
            this_game = getattr(drive, "game_id")
            if game == this_game:
                game_drives += 1
            else:
                drives_per_game +=[game_drives]
                game = this_game
                game_drives = 1
            drive_points, on_offense = self.__drive_scoring(name, drive, turn_over=turn_over)
            if isinstance(drive_points, str):
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
        np_drives_per_game = np.array(drives_per_game)

        ppd = {}
        ppd['offense'] = (np.mean(np_offense_results), np.var(np_offense_results))
        ppd['defense'] = (np.mean(np_defense_results), np.var(np_defense_results))
        ppd['dpg'] = (np.mean(np_drives_per_game), np.var(np_drives_per_game))

        return ppd

    def predict(self, home_team, away_team, timeline=[datetime.now().year - 4, datetime.now().year - 1], predicted_game=None):

        # Type and value checking for unique inputs
        if not isinstance(home_team, team.Team):
            raise TypeError("home_team must be an instance of the Team class, but is " + str(type(home_team)))
        if not isinstance(away_team, team.Team):
            raise TypeError("away_team must be an instance of the Team class, but is " + str(type(away_team)))
        if not isinstance(timeline, list):
            raise TypeError("timeline must be a list, but is " + str(type(timeline)))
        elif len(timeline) != 2:
            raise ValueError("timeline must contain only 2 values, but contains " + str(len(timeline)))
        elif not (isinstance(timeline[0], int) and isinstance(timeline[1], int)):
            raise TypeError("values in timeline must be int, but are " + str(type(timeline[0])) + " and " + str(type(timeline[1])))
        elif timeline[0] > timeline[1]:
            raise ValueError("timeline[0] must be < timeline[1], but timeline[0] = " + str(timeline[0]) + " and timeline[1] = " + str(timeline[1]))
        if predicted_game is not None and not isinstance(predicted_game, int):
            print("NOTE: I actually have no idea what this type is supposed to be....")
            raise TypeError("predicted_game must be int, but is " + str(type(predicted_game)))

        self.home_team = home_team
        self.away_team = away_team

        # self.home_team.get_drive_data(timeline=timeline)
        self.home_team.get_drive_data(timeline=[2005, 2018]) # * for model analysis only

        # self.away_team.get_drive_data(timeline=timeline)
        self.away_team.get_drive_data(timeline=[2005, 2018]) # * for model analysis only

        home_team_drive_dists = self.__ppd_dists(self.home_team.name, self.home_team.drive_data, timeline, predicted_game=predicted_game)
        away_team_drive_dists = self.__ppd_dists(self.away_team.name, self.away_team.drive_data, timeline, predicted_game=predicted_game)

        home_score_hist, away_score_hist = self.__predict_score(home_team_drive_dists['hist'], away_team_drive_dists['hist'])
        home_score_recent, away_score_recent = self.__predict_score(home_team_drive_dists['recent'], away_team_drive_dists['recent'])
        home_score_current, away_score_current = self.__predict_score(home_team_drive_dists['current'], away_team_drive_dists['current'])
        
        home_score_mean = self.weights[0] * home_score_hist[0] + self.weights[1] * home_score_recent[0] + self.weights[2] * home_score_current[0]
        home_score_var =(self.weights[0] ** 2.0) * home_score_hist[1] + (self.weights[1] ** 2.0) * home_score_recent[1] + (self.weights[2] ** 2.0) * home_score_current[1]

        away_score_mean = self.weights[0] * away_score_hist[0] + self.weights[1] * away_score_recent[0] + self.weights[2] * away_score_current[0]
        away_score_var =(self.weights[0] ** 2.0) * away_score_hist[1] + (self.weights[1] ** 2.0) * away_score_recent[1] + (self.weights[2] ** 2.0) * away_score_current[1]

        self.dist_home_team_score = (home_score_mean, home_score_var)
        self.dist_away_team_score = (away_score_mean, away_score_var)

        self.total = (home_score_mean + away_score_mean, home_score_var + away_score_var)
        self.diff = (home_score_mean + self.home_field - away_score_mean, home_score_var + away_score_var)
        return self.total, self.diff
