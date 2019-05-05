import os
from git_cfb import model


data_dir = os.path.join(os.getcwd(), "data")
image_dir = os.path.join(os.getcwd(), "images")
away_team = "Mississippi State"
home_team = "Ole Miss"
model.matchup(home_team, away_team, line = +32, over_under = 38, model='ppd', weights = [0.15, 0.35, 0.5], home_field=3.0)