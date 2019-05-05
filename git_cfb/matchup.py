import os

import numpy as np
from scipy.stats import norm
from . import team

'''
    TODO: refactoring:
        1. no private functions should have var=var arguments
            defaults handled by outward facing functions
'''

class Matchup:
    home_team = None
    away_team = None
    model = None
    data_dir = os.path.join(os.getcwd(), 'data')

    def __init__(self, home_team_name, away_team_name, model, data_dir=None):
        '''
            TODO: input checking:
                1. home_team and away_team are strings
                2. model is an instance of Model
                    a. check for specific functions like "predict"
                3. if data_dir is not None, add logic to ensure data_dir:
                    a. is a path
                    b. exists
                    c. create the passed data_dir if it doesn't exist
                    d. only assign self.data_dir if data
        '''
        self.home_team = team.Team(home_team_name, data_dir=data_dir)
        self.away_team = team.Team(away_team_name, data_dir=data_dir)
        self.model = model
        if data_dir is not None:
            self.data_dir = data_dir

    def analyze(self, line=None, over_under=None):
        '''
            TODO: input checking:
                1. line should be a float
                2. over_under should be a positive, non-zero float
        '''

        total, diff = self.model.predict(self.home_team, self.away_team)
        prob_away_win = norm.cdf(0.0, diff[0], np.sqrt(diff[1]))
        prob_home_win = 1.0 - prob_away_win
        mean_home_score = total[0] / 2.0 + diff[0]
        mean_away_score = total[0] / 2.0 - diff[0]
        print(self.home_team.name + " wins with p=%.4f" % prob_home_win)
        print(self.away_team.name + " wins with p=%.4f" % prob_away_win)
        print("    Predicted score: %.0f - %.0f" % (mean_home_score, mean_away_score))
        if line is not None:
            away_covers = norm.cdf(-1.0 * line, diff[0], np.sqrt(diff[1]))
            home_covers = 1.0 - away_covers
            print("\n" + self.home_team.name + " covers with p=%.4f" % home_covers)
            print(self.away_team.name + " covers with p=%.4f" % away_covers)
        if over_under is not None:
            under_prob = norm.cdf(over_under, total[0], np.sqrt(total[1]))
            over_prob = 1.0 - under_prob
            print("\nover hits with p=%.4f" % over_prob)
            print("under hits with p=%.4f" % under_prob)
