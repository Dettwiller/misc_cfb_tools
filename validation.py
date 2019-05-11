import os
from git_cfb import fetch_data

'''
    TODO: determine the scope of the validation effort:
        1. what teams will be involved?
        2. what years will be involved?
    TODO: Automate validation
        1. get model data for the scope of validation
        2. get validation (game) data for the scope of validation
        3. predict each game
            a. determine probabilities for each actual score
            b. determine predicted winner
        4. look at the distribution of probabilities
        5. error table for predicted winner
    TODO: Tune the model
        1. set up optimization
        2. maximize % correct winners?
        3. maximize probability of correct winner
        4. minimize standard deviation of predicted scores
        5. drive differential and total probabilities to 0.5 (accuracy)
        6. multiobjective of 5 and 4
'''
data_dir = os.path.join(os.getcwd(), "data")

game_data = fetch_data.get_game_data(timeline=[2008, 2018], data_dir=data_dir)