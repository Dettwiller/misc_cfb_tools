import os
from git_cfb import viz


data_dir = os.path.join(os.getcwd(), "data")
image_dir = os.path.join(os.getcwd(), "images")
# viz.plot_team_feature("Alabama", "points_scored", data_dir=data_dir, image_dir=image_dir, titlesize=14, labelsize= 12, ticksize=6, figsize=(12, 6))
# viz.plot_team_feature("Alabama", "points_allowed", data_dir=data_dir, image_dir=image_dir, titlesize=14, labelsize= 12, ticksize=6, figsize=(12, 6))
# viz.plot_team_feature("Alabama", "point_diff", data_dir=data_dir, image_dir=image_dir, titlesize=14, labelsize= 12, ticksize=6, figsize=(12, 6))

viz.plot_team_compare("Ole Miss", "Mississippi State", "point_diff", data_dir=data_dir, image_dir=image_dir, titlesize=14, labelsize= 12, ticksize=6, figsize=(12, 6))