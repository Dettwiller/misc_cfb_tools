import os
from git_cfb import model
# from git_cfb import viz
from scipy.stats import norm


data_dir = os.path.join(os.getcwd(), "data")
image_dir = os.path.join(os.getcwd(), "images")
# viz.plot_team_feature("Alabama", "points_scored", data_dir=data_dir, image_dir=image_dir, titlesize=14, labelsize= 12, ticksize=6, figsize=(12, 6))
# viz.plot_team_feature("Alabama", "points_allowed", data_dir=data_dir, image_dir=image_dir, titlesize=14, labelsize= 12, ticksize=6, figsize=(12, 6))
# viz.plot_team_feature("Alabama", "point_diff", data_dir=data_dir, image_dir=image_dir, titlesize=14, labelsize= 12, ticksize=6, figsize=(12, 6))

# viz.plot_team_compare("Ole Miss", "Mississippi State", "point_diff", data_dir=data_dir, image_dir=image_dir, titlesize=14, labelsize= 12, ticksize=6, figsize=(12, 6))
away_team = "Mississippi State"
home_team = "Ole Miss"
# total, diff = model.ppd_model(home_team, away_team, weights = [0.15, 0.35, 0.5], home_field=0.0, data_dir=data_dir)
model.matchup(home_team, away_team, line = +32, over_under = 38, model='ppd', weights = [0.05, 0.15, 0.8], home_field=0.0)

# print(team_A_data)