import os
from git_cfb import model, matchup


data_dir = os.path.join(os.getcwd(), "data")
image_dir = os.path.join(os.getcwd(), "images")
away_team = "Mississippi State"
home_team = "Ole Miss"

ppd_model = model.PPD_Model(weights = [0.15, 0.35, 0.5], home_field=0.0, data_dir=data_dir)
game = matchup.Matchup(home_team, away_team, ppd_model, data_dir=data_dir)
game.analyze(line = 32, over_under=38)