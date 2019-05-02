import os
import numpy as np
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

def ppd_model(team_A_name, team_B_name, data_dir=os.getcwd()):
    team_A = team.Team(team_A_name, data_dir=data_dir)
    team_B = team.Team(team_B_name, data_dir=data_dir)
    team_A.calc_ppd_dist()
    team_B.calc_ppd_dist()

    # * distribution of team A score = (normal(A offense ppd) + normal(B defense ppd)) * (normal(A offense dpg) + normal(B defense dpg))
    # * distribution of team B score = (normal(B offense ppd) + normal(A defense ppd)) * (normal(B offense dpg) + normal(A defense dpg))
    # * distribution of total points = dist(team A score) + dist(team B score)
    # * distribution of differential = dist(team A score) - dist(team B score)
    team_A_score = (team_A.ppd['oppd_3s'] + team_B.ppd['dppd_3s']) * (team_A.ppd['odpg_3s'] + team_B.ppd['ddpg_3s'])
    team_B_score = (team_B.ppd['oppd_3s'] + team_A.ppd['dppd_3s']) * (team_B.ppd['odpg_3s'] + team_A.ppd['ddpg_3s'])

    diff = team_A_score - team_B_score

    print(team_A.ppd)
    print(team_B.ppd)
