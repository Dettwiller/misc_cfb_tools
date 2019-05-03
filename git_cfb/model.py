import os
import numpy as np
from scipy.stats import norm
from . import fetch_data, utility, team
'''
    The overall goal of this series of functions is 
    to provide models for predicting game outcomes.

    TODO: build a point-per-drive and drives-per-game
    model
        ppd historicall (3 seasons)?
        ppd this season?
        ppd past 3 games?

    TODO: what fetch_data functions do we need?
        fetch based on conference?
        fetch based on team?
        fetch based on season?
    we want to be arbitrary with this, so likely
    not based on team. Maybe the whole season?
    Every game for the entire season with a 
    class for every team?
    Plan of action:
        Pull down drive data for a team
        populate team classes based on data
        matchup function takes in two teams and
        predicts scores
            any new features of the model added
            to team

    TODO: Build team class factory

    TODO: This can be facilitated by robust methods for
    testing arbitrary models with error table
    outcomes
'''
# model.matchup(home_team, away_team, line = -3.5, over_under = 60.5, model='ppd', weights = [0.15, 0.35, 0.5], home_field=0.0)
def matchup(home_team_name, away_team_name, line = None, over_under = None, model='ppd', data_dir=os.path.join(os.getcwd(), 'data'), **kwargs):
    '''
        line: betting line for the HOME team (line = -3.5 indicates home team is favored by 3.5)
        over_under: betting line for total points
        model: the model desired to predict outcome (only ppd for now)
    '''
    if model == 'ppd':
        ppd_args = utility.ppd_kwargs_filter(kwargs)
        total, diff = ppd_model(home_team_name, away_team_name, weights = ppd_args['weights'], home_field=ppd_args['home_field'], data_dir=data_dir)
    # * if the diff is +, home team won

    prob_away_win = norm.cdf(0.0, diff[0], np.sqrt(diff[1]))
    prob_home_win = 1.0 - prob_away_win
    mean_home_score = total[0] / 2.0 + diff[0]
    mean_away_score = total[0] / 2.0 - diff[0]
    print(home_team_name + " wins with p=%.4f" % prob_home_win)
    print(away_team_name + " wins with p=%.4f" % prob_away_win)
    print("    Predicted score: %.0f - %.0f" % (mean_home_score, mean_away_score))
    if line:
        away_covers = norm.cdf(-1.0 * line, diff[0], np.sqrt(diff[1]))
        home_covers = 1.0 - away_covers
        print("\n" + home_team_name + " covers with p=%.4f" % home_covers)
        print(away_team_name + " covers with p=%.4f" % away_covers)
    if over_under:
        under_prob = norm.cdf(over_under, total[0], np.sqrt(total[1]))
        over_prob = 1.0 - under_prob
        print("\nover hits with p=%.4f" % over_prob)
        print("under hits with p=%.4f" % under_prob)

def ppd_model(home_team_name, away_team_name, weights = [0.15, 0.35, 0.5], home_field = 0.3, data_dir=os.path.join(os.getcwd(), 'data')):
    '''
        weights explanation:
            weights[0]: weight given to historical (last 3 seasons) data
            weights[1]: weight given to recent (this season) data
            weights[2]: weight given to current (past 3 games) data
        home_field: the additional points given to the home team for being at home
    '''
    assert(sum(weights) == 1)
    home_team = team.Team(home_team_name, data_dir=data_dir)
    away_team = team.Team(away_team_name, data_dir=data_dir)
    home_team.calc_ppd_dists()
    away_team.calc_ppd_dists()

    score_home_hist, score_away_hist = utility.pred_score(home_team.drive_dists['hist'], away_team.drive_dists['hist'])
    score_home_recent, score_away_recent = utility.pred_score(home_team.drive_dists['recent'], away_team.drive_dists['recent'])
    score_home_current, score_away_current = utility.pred_score(home_team.drive_dists['current'], away_team.drive_dists['current'])

    # * Rules for normal distributions
    # * N(m1, v1) + N(m2, v2) = N(m1 + m2, v1 + v2)
    # * N(m1, v1) - N(m2, v2) = N(m1 - m2, v1 + v2)
    # * a*N(m1, v1) = N( a*m1, (a^2)*v1 ) 

    score_home_mean = weights[0] * score_home_hist[0] + weights[1] * score_home_recent[0] + weights[2] * score_home_current[0]
    score_home_var =(weights[0] ** 2.0) * score_home_hist[1] + (weights[1] ** 2.0) * score_home_recent[1] + (weights[2] ** 2.0) * score_home_current[1]

    score_away_mean = weights[0] * score_away_hist[0] + weights[1] * score_away_recent[0] + weights[2] * score_away_current[0]
    score_away_var =(weights[0] ** 2.0) * score_away_hist[1] + (weights[1] ** 2.0) * score_away_recent[1] + (weights[2] ** 2.0) * score_away_current[1]
    # print("    " + home_team_name + " mean = " + str(score_home_mean))
    # print("    " + away_team_name + " mean = " + str(score_away_mean))

    # print("    " + home_team_name + " var = " + str(score_home_var))
    # print("    " + away_team_name + " var = " + str(score_away_var))


    total = (score_home_mean + score_away_mean, score_home_var + score_away_var)
    diff = (score_home_mean + home_field - score_away_mean, score_home_var + score_away_var)

    return total, diff
