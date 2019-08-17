from football_modeling.model import Model
import numpy as np
from collections.abc import Iterable
from football_modeling.team import Team
from datetime import datetime
from football_modeling import tools

def ppd_model(weights, ranges, home_field_advantage=0.0):
    model = PPDModel(weights, ranges, home_field_advantage=home_field_advantage)
    return model

class PPDModel(Model):
    '''
    Class for creating a points per drive based model
    
    Args:
        ranges: iterable of 3 entries corresoponding to:
                [years of historical data, seasons of recent data, and games of current data]

        weights: iterable of 3 entries corresponding to the weight given to each range:
                [historical, recent, current]

        home_field_advantage: additional points given to the home team
    '''
    def __init__(self, weights, ranges, home_field_advantage=0.0):
        Model.__init__(self, weights, ranges, home_field_advantage=home_field_advantage)

    def __get_current_season(self, data_df, timeline, predicted_game_id):
        # * candidate for moving to model.Model
        seasons = []
        for i in range(timeline[0], timeline[1] + 1):
            seasons += [i]
        if predicted_game_id:
            if predicted_game_id in data_df["game_id"].values:
                i_predicted_game_first_drive = data_df[data_df["game_id"] == predicted_game_id].index[0]
            else:
                previous_game_id = 0
                for game_id in data_df["game_id"].values:
                    if int(game_id) > previous_game_id and int(game_id) < predicted_game_id:
                        previous_game_id = int(game_id)
                i_predicted_game_first_drive = data_df[data_df['game_id'] == previous_game_id].index[0]
            current_season = int(data_df["season"].iloc[i_predicted_game_first_drive])
        else:
            current_season = seasons[-1]
        return current_season

    def __drive_scoring(self, drive, team_name, turn_over):
        non_scoring_results = ["PUNT", "DOWNS", "END OF HALF", "END OF GAME", "END OF 4TH QUARTER"]
        td_results = ["PASSING TD", "RUSHING TD", "TD"]
        fg_results = ["FG GOOD", "FG"]
        drive_result = getattr(drive, "drive_result")
        if drive_result in td_results:
            points = 7
        elif drive_result in fg_results:
            points = 3
        elif drive_result == "SF":
            points = -2
        elif drive_result in non_scoring_results or turn_over:
            points = 0
        else:
            print("unknown drive result: " + drive_result)
            points = drive_result
        on_offense = getattr(drive, "offense") == team_name
        return points, on_offense

    def __calculate_ppd(self, drives_df, team_name):
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
                drives_per_game += [game_drives]
                game = this_game
                game_drives = 1
            drive_points, on_offense = self.__drive_scoring(drive, team_name, turn_over)
            if isinstance(drive_points, str):
                turn_over = True
            elif on_offense and not turn_over:
                offense_results += [drive_points]
                turn_over = False
            elif not on_offense and not turn_over:
                defense_results += [-1 * drive_points]
                turn_over = False
            elif not on_offense and turn_over:
                offense_results += [-1 * drive_points]
                defense_results += [-1 * drive_points]
                turn_over = False
            elif on_offense and turn_over:
                defense_results += [drive_points]
                offense_results += [drive_points]
                turn_over = False
        
        np_offense_results = np.array(offense_results)
        np_defense_results = np.array(defense_results)
        np_drives_per_game = np.array(drives_per_game)

        team_ppd = {}
        team_ppd['offense'] = (np.mean(np_offense_results), np.var(np_offense_results))
        team_ppd['defense'] = (np.mean(np_defense_results), np.var(np_defense_results))
        team_ppd['dpg'] = (np.mean(np_drives_per_game), np.var(np_drives_per_game))
        return team_ppd

    def __weight_ppd_dists(self, ppd_dist, weight_index):
        weighted_ppd = {
            'offense': (
                self.weights[weight_index] * ppd_dist['offense'][weight_index],
                (self.weights[weight_index] ** 2) * ppd_dist['offense'][1]
                ),
            'defense': (
                self.weights[weight_index] * ppd_dist['defense'][weight_index],
                (self.weights[weight_index] ** 2) * ppd_dist['defense'][1]
                ),
            'dpg': (
                self.weights[weight_index] * ppd_dist['dpg'][weight_index],
                (self.weights[weight_index] ** 2) * ppd_dist['dpg'][1]
                )
        }
        return weighted_ppd


    def __ppd_dists(self, team_drive_data, team_name, timeline, predicted_game_id):
        current_season = self.__get_current_season(team_drive_data, timeline, predicted_game_id)
        hist_data = self._get_historical_data(current_season, team_drive_data)
        recent_data = self._get_recent_data(current_season, team_drive_data)
        current_data = self._get_current_data(team_drive_data, predicted_game_id)

        hist_ppd = self.__calculate_ppd(hist_data, team_name)
        recent_ppd = self.__calculate_ppd(recent_data, team_name)
        current_ppd = self.__calculate_ppd(current_data, team_name)

        weighted_hist_ppd = self.__weight_ppd_dists(hist_ppd, 0)
        weighted_recent_ppd = self.__weight_ppd_dists(recent_ppd, 1)
        weighted_current_ppd = self.__weight_ppd_dists(current_ppd, 2)

        offense_ppd = [weighted_hist_ppd['offense'], weighted_recent_ppd['offense'], weighted_current_ppd['offense']]
        defense_ppd = [weighted_hist_ppd['defense'], weighted_recent_ppd['defense'], weighted_current_ppd['defense']]
        dpg = [weighted_hist_ppd['dpg'], weighted_recent_ppd['dpg'], weighted_current_ppd['dpg']]

        average_offense_ppd = tools.average_gaussian_distributions(offense_ppd)
        average_defense_ppd = tools.average_gaussian_distributions(defense_ppd)
        average_dpg = tools.average_gaussian_distributions(dpg)

        ppd_dists = {'offense': average_offense_ppd, 'defense': average_defense_ppd, 'dpg': average_dpg}
        return ppd_dists

    def __score_dists(self, home_team_drive_dists, away_team_drive_dists):
        # TODO MOve the ppd into __ppd function and then break up __ppd function into components
        # TODO or not and just rename the __ppd function appropriately
        home_ppd = tools.average_gaussian_distributions(
            [home_team_drive_dists['offense'], away_team_drive_dists['defense']]
        )

        away_ppd = tools.average_gaussian_distributions(
            [away_team_drive_dists['offense'], home_team_drive_dists['defense']]
        )

        dpg = tools.average_gaussian_distributions(
            [home_team_drive_dists['dpg'], away_team_drive_dists['dpg']]
        )

        home_points = tools.multiply_gaussians(home_ppd, dpg)
        away_points = tools.multiply_gaussians(away_ppd, dpg)
        # TODO: you just finished this function
        return home_points, away_points

    def predict(self, home_team, away_team, timeline=[datetime.now().year-4, datetime.now().year-1], predicted_game_id=0, neutral_site=False, print_progress=False):
        home_team_type_check = isinstance(home_team, Team)
        assert home_team_type_check, "home_team is not an instance of football_modeling.team.Team: %r" % type(home_team)
        away_team_type_check = isinstance(away_team, Team)
        assert away_team_type_check, "away_team is not an instance of football_modeling.team.Team: %r" % type(away_team)
        tools.timeline_check(timeline)
        predicted_game_id_check = isinstance(predicted_game_id, int)
        assert predicted_game_id_check, "predicted_game_id is not an integer: %r" % type(predicted_game_id)
        neutral_site_type_check = isinstance(neutral_site, bool)
        assert neutral_site_type_check, "neutral_site is not bool %r" % type(neutral_site)
        print_progress_type_check = isinstance(print_progress, bool)
        assert print_progress_type_check, "print_progress is not bool: %r" % type(print_progress)

        home_team_drive_data = home_team.get_drive_data(timeline=timeline, print_progress=print_progress)
        away_team_drive_data = away_team.get_drive_data(timeline=timeline, print_progress=print_progress)

        home_team_drive_dists = self.__ppd_dists(home_team_drive_data, home_team.name, timeline, predicted_game_id)
        away_team_drive_dists = self.__ppd_dists(away_team_drive_data, away_team.name, timeline, predicted_game_id) 

        home_team_score_dists, away_team_score_dists = self.__score_dists(home_team_drive_dists, away_team_drive_dists)

        # TODO: Finish predictions based on score_dists