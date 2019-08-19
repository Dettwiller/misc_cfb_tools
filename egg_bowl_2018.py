from os.path import join
from os import getcwd

import numpy as np
from scipy.stats import norm

from football_modeling import ppd_model as ppdm
from football_modeling import team

data_dir = join(getcwd(), "validation_data")
drives_dir = join(getcwd(), "drives_data")
games_dir = join(getcwd(), "games_data")

away_team_name = "Mississippi State"
home_team_name = "Ole Miss"

away_team = team.team(away_team_name, data_dir=data_dir, games_dir=games_dir, drives_dir=drives_dir)
home_team = team.team(home_team_name, data_dir=data_dir, games_dir=games_dir, drives_dir=drives_dir)

weights = [0.025, 0.125, 0.85]
ranges = [5, 1, 3]
hfa = 0.0
timeline = [2013, 2018]

ppd_model = ppdm.ppd_model(weights, ranges, home_field_advantage=hfa)
total_dist, spread_dist = ppd_model.predict(home_team, away_team, timeline=timeline, predicted_game_id=401012349, print_progress=True) 

prob_away_win = norm.cdf(0.0, spread_dist[0], np.sqrt(spread_dist[1]))
prob_home_win = 1.0 - prob_away_win
mean_home_score = (total_dist[0] + spread_dist[0]) / 2
mean_away_score = (total_dist[0] - spread_dist[0]) / 2
print(home_team.name + " wins with p=%.4f" % prob_home_win)
print(away_team.name + " wins with p=%.4f" % prob_away_win)
print("    Predicted spread: %.4f" % spread_dist[0])
print("    Predicted score: %.0f to %.0f" % (mean_home_score, mean_away_score))
print("    Predicted total: %.2f" % total_dist[0])

prob_actual_total = norm.cdf(38, total_dist[0], np.sqrt(total_dist[1]))
prob_actual_spread = norm.cdf(-32, spread_dist[0], np.sqrt(spread_dist[1]))
print("Probability of actual total (38pts) = %.4f" % prob_actual_total)
print("Probability of actual spread (32pts) = %.4f" % prob_actual_spread)

# game.analyze(line = 32, over_under=38)
