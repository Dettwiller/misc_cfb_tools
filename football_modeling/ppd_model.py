from football_modeling.model import Model
import numpy as np
from collections.abc import Iterable
from football_modeling.team import Team
from datetime import datetime
from football_modeling import tools

def ppd_model(weights, home_field_advantage=0.0):
    model = PPDModel(weights, home_field_advantage=home_field_advantage)
    return model

class PPDModel(Model):
    def __init__(self, weights, home_field_advantage=0.0):
        weights_type_check = isinstance(weights, Iterable)
        assert weights_type_check, "weights is not iterable: %r" % weights
        weights_sum_check = abs(sum(weights) - 1.0) < 1e-8
        assert weights_sum_check, "weights do not sum to 1+-1e-8: %r" % weights_sum_check
        weights_sign_check = all([weight >= 0.0 for weight in weights])
        assert weights_sign_check, "weights are not all >= 0.0: %r" % weights
        Model.__init__(self, home_field_advantage=home_field_advantage)
        self.weights = weights

    def __ppd_dist(self, team_drive_data):
        pass

    def __score_dist(self, home_team_drive_dists, away_team_drive_dists):
        pass

    def predict(self, home_team, away_team, timeline=[datetime.now().year-4, datetime.now().year-1], neutral_site=False, print_progress=False):
        home_team_type_check = isinstance(home_team, Team)
        assert home_team_type_check, "home_team must be instance of football_modeling.team.Team: %r" % type(home_team)
        away_team_type_check = isinstance(away_team, Team)
        assert away_team_type_check, "away_team must be instance of football_modeling.team.Team: %r" % type(away_team)
        tools.timeline_check(timeline)
        neutral_site_type_check = isinstance(neutral_site, bool)
        assert neutral_site_type_check, "neutral_site is not bool %r" % type(neutral_site)
        print_progress_type_check = isinstance(print_progress, bool)
        assert print_progress_type_check, "print_progress is not bool: %r" % type(print_progress)

        home_team_drive_data = home_team.get_drive_data(timeline=timeline, print_progress=print_progress)
        away_team_drive_data = away_team.get_drive_data(timeline=timeline, print_progress=print_progress)

        home_team_drive_dists = self.__ppd_dist(home_team_drive_data) # TODO: define this in PPDModel
        away_team_drive_dists = self.__ppd_dist(away_team_drive_data) # TODO: define this in PPDModel

        home_team_score_dists = self.__score_dist(home_team_drive_dists, away_team_drive_dists) # TODO: define this in PPDModel
        away_team_score_dists = self.__score_dist(away_team_drive_dists, home_team_drive_dists) # TODO: define this in PPDModel

        # TODO: Finish predictions based on score_dists