from collections import namedtuple
from datetime import datetime
from os import getcwd
from os.path import join, isfile

import numpy as np
import requests
from scipy.stats import norm

from football_modeling import ppd_model, team, tools, fetch_data

def prediction_analysis(total_dist, spread_dist, total, spread, home_win_odds, model_results_dir):
    Prediction = namedtuple("Prediction", "prediction difference probability confidence ts_confidence")
    pred_spread = spread_dist[0]
    pred_total = total_dist[0]
    # pred_home_points = (total_dist[0] + spread_dist[0]) / 2
    # pred_away_points = (total_dist[0] - spread_dist[0]) / 2
    total_diff = pred_total - total # positive total_diff = bet over, negative total_diff = bet under
    spread_diff = -pred_spread - spread # negative sign gets it to odds format
                                        # positive spread_diff = bet home_spread, negative spread_diff = bet away_spread

    prob_away_win = norm.cdf(0.0, spread_dist[0], np.sqrt(spread_dist[1]))
    prob_home_win = 1.0 - prob_away_win
    winner_prob = max(prob_away_win, prob_home_win)
    if home_win_odds < 0: # home team favored
        if prob_home_win > 0.5: # home team predicted win
            win_diff = 0 # agreement
        else:
            win_diff = -1 # disagreement, bet on away team
    elif home_win_odds > 0: # away team favored
        if prob_away_win > 0.5: # away team predicted win
            win_diff = 0 # agreement
        else:
            win_diff = 1 # disagreement, bet on home team
    else: # home odds are EVEN
        if prob_home_win > 0.5: # home team predicted win
            win_diff = 1 # disagreement, bet on home team
        elif prob_away_win > 0.5: # away team predicted win
            win_diff = -1 # disagreement, bet on away team
        else: # predicted EVEN
            win_diff = 0 # lol predicted tie on even spread


    if total <= total_dist[0]:
        # prob_total = norm.cdf(total, total_dist[0], np.sqrt(total_dist[1])) * 2.0 # 2 sided probability of score
        prob_total = 1.0 - norm.cdf(total, total_dist[0], np.sqrt(total_dist[1])) # probability of bet win
    else:
        # prob_total = (1.0 - norm.cdf(total, total_dist[0], np.sqrt(total_dist[1]))) * 2.0 # 2 sided probability of score
         prob_total = norm.cdf(total, total_dist[0], np.sqrt(total_dist[1])) # probability of bet win

    if spread <= spread_dist[0]:
        # prob_spread = norm.cdf(spread, spread_dist[0], np.sqrt(spread_dist[1])) * 2.0 # 2 sided probability of score
        prob_spread = 1.0 - norm.cdf(spread, spread_dist[0], np.sqrt(spread_dist[1])) # probability of bet win
    else:
        # prob_spread = (1.0 - norm.cdf(spread, spread_dist[0], np.sqrt(spread_dist[1]))) * 2.0 # 2 sided probability of score
        prob_spread = norm.cdf(spread, spread_dist[0], np.sqrt(spread_dist[1])) # probability of bet win

    n_games = 0
    win_successes = 0
    win_prob_count = 0
    spread_successes = 0
    ts_spread_successes = 0
    total_successes = 0
    ts_total_successes = 0
    with open(join(model_results_dir, "results.csv"), 'r', encoding='utf-8') as mrf:
        line = mrf.readline() # header
        # season, game_id, home_team, away_team, neutral_site, home_score, away_score,
        # pred_home_score, pred_away_score, prob_winner, prob_spread, prob_total,
        # total_error, spread_error, home_error, away_error
        line = mrf.readline() # content
        while line:
            list_line = line.strip().split(',')
            spread_error = float(list_line[13])
            total_error = float(list_line[12])
            prob_winner = float(list_line[9])
            # home_margin = float(list_line[5]) - float(list_line[6])
            # if spread_error > 0.0: # prediction > spread line, winning bet when prediction - true > preadiction - spread
            if total_diff > 0.0 and total_error < total_diff: # ppd prediciton > O/U line and ppd prediction - true toal < ppd prediction - O/U line
                total_successes += 1
            elif total_diff < 0.0 and total_error < -total_diff:
                total_successes += 1
            if abs(total_error) < abs(total_diff):
                ts_total_successes += 1
            if spread_diff > 0.0 and spread_error > -spread_diff: # -(pred_home - pred_away) {pred_home_spread} > 0.0 and pred_home_spread > -true_home_spread
                spread_successes += 1
            elif spread_diff < 0.0 and spread_error < -spread_diff:
                spread_successes += 1
            if abs(spread_error) < abs(spread_diff):
                ts_spread_successes += 1
            if prob_winner > 0.5 and prob_winner >= winner_prob: # correct win prediction and with probability >= current winner probabiltiy
                win_successes += 1
                win_prob_count += 1
            elif prob_winner < 0.5 and (1 - prob_winner) >= winner_prob: # wrong win prediction with probability >= current winner probability
                win_prob_count += 1
            n_games += 1
            line = mrf.readline()
    spread_confidence = 100 * float(spread_successes) / float(n_games) # the percentage of games with spread errors still resulting in a win for the suggested bet
    total_confidence = 100 * float(total_successes) / float(n_games) # the percentage of games with total errors still resulting in a win for the suggested bet
    win_confidence = 100 * float(win_successes) / float(win_prob_count) # the percentage of games with corectly predicted winners at this win probability
    two_sided_spread_confidence = 100 * float(ts_spread_successes) / float(n_games)
    two_sided_total_confidence = 100 * float(ts_total_successes) / float(n_games)

    spread_predictions = Prediction(spread_dist[0], spread_diff, prob_spread, spread_confidence, two_sided_spread_confidence)
    total_predictions = Prediction(total_dist[0], total_diff, prob_total, total_confidence, two_sided_total_confidence)
    win_predictions = Prediction(winner_prob, win_diff, winner_prob, win_confidence, 0)  # win_diff 1 = disagree with odds in favor of home team
                                                                                         # win_diff -1 = disagree with odds in favor of away team
    return spread_predictions, total_predictions, win_predictions

def analyze_matchup(game, eval_model, data_dir, model_results_dir, recruiting_dir, spread_file, total_file, win_file):
    # 'date' 'neutral_site' 'away_team' 'home_team' 'home_spread' 'away_spread_odds'
    # 'home_spread_odds' 'away_win_odds' 'home_win_odds' 'total' 'over_odds' 'under_odds'
    away_team = team.team(game.away_team, drives_dir=data_dir, recruiting_dir=recruiting_dir)
    home_team = team.team(game.home_team, drives_dir=data_dir, recruiting_dir=recruiting_dir)
    # print("got teams") #DEBUG
    # total_dist, spread_dist = eval_model.predict(home_team, away_team, neutral_site=game.neutral_site, print_progress=True)
    total_dist, spread_dist = eval_model.predict(home_team, away_team, neutral_site=game.neutral_site)
    # print("got dists") #DEBUG
    spread, total, win = prediction_analysis(total_dist, spread_dist, game.total, game.home_spread, game.home_win_odds, model_results_dir)
    # print("analyzed pred") #DEBUG
    # spread_header = "matchup,date,home line,home odds,away odds,diff (pos = home bet, neg = away bet),probability,confidence\n"
    spread_line_list = [
        game.away_team + " @ " + game.home_team, game.date.strftime("%m/%d/%Y"),
        str(game.home_spread), str(game.home_spread_odds), str(game.away_spread_odds),
        str(-spread.prediction), str(spread.probability), str(spread.confidence),
        str(spread.ts_confidence)
    ]
    # total_header = "matchup,date,O/U,over odds,under odds,diff (pos = over bet, neg = under bet),probability,confidence\n"
    total_line_list = [
        game.away_team + " @ " + game.home_team, game.date.strftime("%m/%d/%Y"),
        str(game.total), str(game.over_odds), str(game.under_odds),
        str(total.prediction), str(total.probability), str(total.confidence),
        str(total.ts_confidence)
    ]
    # win_header = "matchup,date,home odds,away odds,diff (1 = favor home, -1 = favor away, 0 = agree),probability,confidence\n"
    win_line_list = [
        game.away_team + " @ " + game.home_team, game.date.strftime("%m/%d/%Y"),
        str(game.home_win_odds), str(game.away_win_odds),
        str(win.difference), str(win.prediction), str(win.confidence)
    ]

    with open(spread_file, 'a', encoding='utf-8') as sf:
        sf.write(','.join(spread_line_list) + "\n")

    with open(total_file, 'a', encoding='utf-8') as tf:
        tf.write(','.join(total_line_list) + "\n")

    with open(win_file, 'a', encoding='utf-8') as wf:
        wf.write(','.join(win_line_list) + "\n")

if __name__ == "__main__":
    weights = [0.01, 0.09, 0.9]
    ranges = [3, 1, 3]
    hfa = 0.0

    str_date = datetime.now().strftime("%m-%d-%Y")
    spread_filename = str_date + "_spread.csv"
    total_filename = str_date + "_total.csv"
    win_filename = str_date + "_win.csv"

    prediction_dir = join(getcwd(), 'prediction_data')
    drives_dir = join(getcwd(), 'drives_data')
    recruiting_dir = join(getcwd(), 'recruiting_data')
    model_results_dir = join(getcwd(), 'validation_data')

    spread_header = "matchup,date,home line,home odds,away odds,predicted,probability,confidence,2s confidence\n"
    total_header = "matchup,date,O/U,over odds,under odds,predicted,probability,confidence,2s confidence\n"
    win_header = "matchup,date,home odds,away odds,diff (1 = favor home | -1 = favor away | 0 = agree),probability,confidence\n"

    spread_file = join(prediction_dir, spread_filename)
    total_file = join(prediction_dir, total_filename)
    win_file = join(prediction_dir, win_filename)

    if not isfile(spread_file):
        with open(spread_file, 'w+', encoding='utf-8') as sf:
            sf.write(spread_header)

    if not isfile(total_file):
        with open(total_file, 'w+', encoding='utf-8') as tf:
            tf.write(total_header)

    if not isfile(win_file):
        with open(win_file, 'w+', encoding='utf-8') as wf:
            wf.write(win_header)

    # Matchup = namedtuple('Matchup', 'date neutral_site away_team home_team home_spread away_spread_odds home_spread_odds away_win_odds home_win_odds total over_odds under_odds')
    # game_1 = Matchup(datetime(2019, 8, 24), True, 'Florida', 'Miami', 7.5, -115, -105, -290, 240, 47, -110, -110)
    # game_2 = Matchup(datetime(2019, 8, 24), False, 'Arizona', "Hawai'i", 11, -110, -110, -420, 310, 74, -110, -110)

    cfb_downloader = fetch_data.data_downloader()
    fbs_teams_df = cfb_downloader.get_all_fbs_teams()
    fbs_teams_list = fbs_teams_df['school'].tolist()

    available_games = tools.get_cfb_odds(fbs_teams_list)

    eval_model = ppd_model.ppd_model(weights, ranges, home_field_advantage=hfa)

    for game in available_games:
    # for game in [available_games[0]]:
        # analyze_matchup(game, eval_model, drives_dir, model_results_dir, spread_file, total_file, win_file)
        trying = True
        while trying:
            print("attempting " + game.away_team + " @ " + game.home_team)
            try:
                analyze_matchup(game, eval_model, drives_dir, model_results_dir, recruiting_dir, spread_file, total_file, win_file)
                print("    accomplished " + game.away_team + " @ " + game.home_team)
                trying = False
            except Exception as ex:
                print("    failed " + game.away_team + " @ " + game.home_team)
                print(ex)
                trying = False

    # TODO execute ppd model on each matchup
    # TODO calculate any helpful probabilities (prob_spread, prob_total, and percentiles of those probabilities (model is rarely this wrong sort of thing))
    # TODO all the relevant stuff to a csv
    # TODO: analysis_date.csv: away team @ home team, home team spread, home team spread odds, away team spread odds, home team moneyline odds,
    # TODO                      away team moneyline odds, total points, over odds, under odds, pred_spread, prob_spread, prob_prob_spread,
    # TODO:                     prob_winner, prob_prob_winner, pred_total, prob_total, prob_prob_total, home spread bet, away spread bet,
    # TODO:                     home moneyline bet, away moneyline bet, over bet, under bet
    # TODO: instead of probabilities calcualted from normals, just count the aboves and belows from the validation_data
