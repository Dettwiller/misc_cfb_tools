from collections.abc import Iterable
from datetime import datetime
from warnings import warn

import numpy as np

from football_modeling import tools
from football_modeling.model import Model
from football_modeling.team import Team


def ppd_model(weights, ranges, home_field_advantage=0.0):
    model = PPDModel(weights, ranges, home_field_advantage=home_field_advantage)
    return model

class PPDModel(Model):
    '''
    Class for creating a points per drive based model

    Args:
        ranges: iterable of 3 entries corresponding to:
                [years of historical data, seasons of recent data, and games of current data]

        weights: iterable of 3 entries corresponding to the weight given to each range:
                [historical, recent, current]

        home_field_advantage: additional points given to the home team
    '''
    def __init__(self, weights, ranges, home_field_advantage=0.0):
        Model.__init__(self, weights, ranges, home_field_advantage=home_field_advantage)
        self.total_adjust = 12.29
        self.timeline = [datetime.now().year - ranges[0], datetime.now().year]

    def __timeline_check(self, timeline):
        if timeline is not None:
            tools.timeline_check(timeline)
            if timeline[0] != self.timeline[0] or timeline[1] != self.timeline[1]:
                warn("new timeline does not match stored timeline, updating stored timeline...")
                self.timeline = timeline

    def __get_current_season(self, data_df, predicted_game_id):
        # * candidate for moving to model.Model
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
            current_season = self.timeline[-1]
        return current_season

    def __drive_scoring(self, drive, team_name, turnover):
        non_scoring_results = [
            "PUNT", "DOWNS", "TURNOVER ON DOWNS", "MISSED FG", "FG MISSED",
            "END OF HALF", "END OF GAME", "END OF 4TH QUARTER", "POSSESSION (FOR OT DRIVES)"
            ]
        offensive_touchdown_results = [
            "PASSING TD", "RUSHING TD", "TD", "END OF HALF TD", "END OF GAME TD"
            ]
        field_goal_results = ["FG GOOD", "FG"]
        no_score_turnover_results = ["INT", "FUMBLE"]
        defensive_touchdown_results = [
            "INT TD", "FUMBLE RETURN TD", "INT RETURN TOUCH", "FUMBLE TD",
            "PUNT TD", "TURNOVER ON DOWNS TD", "DOWNS TD"
            ] # PUNT TD most often blocked punt for defensive TD
        special_teams_results = [
            "PUNT RETURN TD", "KICKOFF", "Uncategorized", "KICKOFF RETURN TD",
            "FG MISSED TD", "MISSED FG TD"
            ] # Uncategorized appears to be kickoffs
        drive_result = getattr(drive, "drive_result")

        drive_turnover = False
        if drive_result in offensive_touchdown_results:
            points = 7
        elif drive_result in field_goal_results:
            points = 3
        elif drive_result == "SF":
            points = -2
        elif drive_result in no_score_turnover_results:
            points = 0
            drive_turnover = True
        elif drive_result in defensive_touchdown_results:
            points = -7
        elif drive_result in special_teams_results:
            points = 0
        elif drive_result in non_scoring_results or turnover:
            points = 0
        else:
            print("unknown drive result: " + drive_result)
            print(drive)
            points = 0
        on_offense = getattr(drive, "offense") == team_name
        return points, on_offense, drive_turnover

    def __calculate_ppd(self, drives_df, team_name):
        turnover = False
        offense_results = []
        defense_results = []
        drives_per_game = []
        game_drives = 0
        game = -1
        for drive in drives_df.itertuples(index=True, name='Drive'):
            this_game = getattr(drive, "game_id")
            if game == this_game:
                game_drives += 1
            elif game != -1:
                drives_per_game += [game_drives]
                game = this_game
                game_drives = 1
            else:
                game = this_game
                game_drives = 1
            drive_points, on_offense, drive_turnover = self.__drive_scoring(drive, team_name, turnover)
            if on_offense and not turnover:
                offense_results += [drive_points]
            elif not on_offense and not turnover:
                defense_results += [-1 * drive_points]
            elif not on_offense and turnover:
                offense_results += [-1 * drive_points]
                defense_results += [-1 * drive_points]
            elif on_offense and turnover:
                defense_results += [drive_points]
                offense_results += [drive_points]
            turnover = drive_turnover
        drives_per_game += [game_drives]
        assert len(offense_results) > 0, "no offense results for " + team_name
        assert len(defense_results) > 0, "no defense results for " + team_name
        assert len(drives_per_game) > 0, "no drives per game results for " + team_name
        np_offense_results = np.array(offense_results)
        np_defense_results = np.array(defense_results)
        np_drives_per_game = np.array(drives_per_game)

        team_ppd = {}
        team_ppd['offense'] = (np.mean(np_offense_results), np.var(np_offense_results))
        team_ppd['defense'] = (np.mean(np_defense_results), np.var(np_defense_results))
        team_ppd['dpg'] = (np.mean(np_drives_per_game), np.var(np_drives_per_game))
        return team_ppd

    def __ppd_dists(self, team_drive_data, team_name, predicted_game_id):
        current_season = self.__get_current_season(team_drive_data, predicted_game_id)
        # print("        got current season") #DEBUG
        hist_data = self._get_historical_data(current_season, team_drive_data)
        # print("        got historical data") #DEBUG
        recent_data = self._get_recent_data(current_season, team_drive_data)
        # print("        got recent data") #DEBUG
        current_data = self._get_current_data(team_drive_data, predicted_game_id)
        # print("        got current data") #DEBUG
        hist_ppd = self.__calculate_ppd(hist_data, team_name)
        # print("        got hist ppd") #DEBUG
        recent_ppd = self.__calculate_ppd(recent_data, team_name)
        # print("        got recent ppd") #DEBUG
        current_ppd = self.__calculate_ppd(current_data, team_name)
        # print("        got current ppd") #DEBUG

        offense_ppd = [hist_ppd['offense'], recent_ppd['offense'], current_ppd['offense']]
        defense_ppd = [hist_ppd['defense'], recent_ppd['defense'], current_ppd['defense']]
        dpg = [hist_ppd['dpg'], recent_ppd['dpg'], current_ppd['dpg']]

        average_offense_ppd = tools.weighted_average_gaussian_distributions(offense_ppd, self.weights)
        # print("        got weighted average offense") #DEBUG
        average_defense_ppd = tools.weighted_average_gaussian_distributions(defense_ppd, self.weights)
        # print("        got weighted average defense") #DEBUG
        average_dpg = tools.weighted_average_gaussian_distributions(dpg, self.weights)
        # print("        got weighted average dpg") #DEBUG

        ppd_dists = {'offense': average_offense_ppd, 'defense': average_defense_ppd, 'dpg': average_dpg}
        return ppd_dists

    def __score_dists(self, away_team_drive_dists, home_team_drive_dists, away_talent_portion, home_talent_portion):
        # full games points accounted for in both offense and defense, so divide by two
        away_ppd = (
            (away_team_drive_dists['offense'][0] - home_team_drive_dists['defense'][0]) / 2.0,
            (away_team_drive_dists['offense'][1] + home_team_drive_dists['defense'][1]) / 4.0 # 2.0^2
        )

        home_ppd = (
            (home_team_drive_dists['offense'][0] - away_team_drive_dists['defense'][0]) / 2.0,
            (home_team_drive_dists['offense'][1] + away_team_drive_dists['defense'][1]) / 4.0 # 2.0^2
        )

        dpg = tools.average_gaussian_distributions(
            [home_team_drive_dists['dpg'], away_team_drive_dists['dpg']]
        )

        away_points = tools.multiply_gaussians(away_ppd, dpg) + away_talent_portion * self.total_adjust
        home_points = tools.multiply_gaussians(home_ppd, dpg) + home_talent_portion * self.total_adjust
        return home_points, away_points

    def predict(self, home_team, away_team, timeline=None, predicted_game_id=0, neutral_site=False, print_progress=False):
        home_team_type_check = isinstance(home_team, Team)
        assert home_team_type_check, "home_team is not an instance of football_modeling.team.Team: %r" % type(home_team)
        away_team_type_check = isinstance(away_team, Team)
        assert away_team_type_check, "away_team is not an instance of football_modeling.team.Team: %r" % type(away_team)
        self.__timeline_check(timeline)
        predicted_game_id_check = isinstance(predicted_game_id, int)
        assert predicted_game_id_check, "predicted_game_id is not an integer: %r" % type(predicted_game_id)
        neutral_site_type_check = isinstance(neutral_site, bool)
        assert neutral_site_type_check, "neutral_site is not bool %r" % type(neutral_site)
        print_progress_type_check = isinstance(print_progress, bool)
        assert print_progress_type_check, "print_progress is not bool: %r" % type(print_progress)

        home_team_drive_data = home_team.get_data(self.timeline, data_type='drives', print_progress=print_progress)
        away_team_drive_data = away_team.get_data(self.timeline, data_type='drives', print_progress=print_progress)
        # print("    got data") #DEBUG
        home_team_drive_dists = self.__ppd_dists(home_team_drive_data, home_team.name, predicted_game_id)
        away_team_drive_dists = self.__ppd_dists(away_team_drive_data, away_team.name, predicted_game_id)
        # print("    got dists") #DEBUG

        away_talent_df = away_team.get_data([datetime.now().year-3, datetime.now().year], data_type='recruiting', print_progress=False)
        home_talent_df = home_team.get_data([datetime.now().year-3, datetime.now().year], data_type='recruiting', print_progress=False)
        away_talent_portion, home_talent_portion = tools.calculate_talent_portion(away_talent_df, home_talent_df)

        home_team_score_dist, away_team_score_dist = self.__score_dists(away_team_drive_dists, home_team_drive_dists, away_talent_portion, home_talent_portion)
        # print("    got scores") #DEBUG
        total_points_dist = (
            home_team_score_dist[0] + away_team_score_dist[0],
            home_team_score_dist[1] + away_team_score_dist[1]
        ) # 12.29 = average underprediction in week 1 and 2

        spread_dist = (
            home_team_score_dist[0] + self.home_field_advantage - away_team_score_dist[0],
            home_team_score_dist[1] + away_team_score_dist[1]
        )

        return total_points_dist, spread_dist
