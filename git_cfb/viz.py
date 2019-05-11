import os
from datetime import datetime

import matplotlib.pyplot as plt

from . import team, utility

def dist_plot(x, f):
    plt.figure("Distribution")
    plt.plot(x, f)
    plt.ylabel("f")
    plt.xlabel("x")


def plot_team_feature(team_name, feature, rolling_average = True, timeline=[1880, datetime.now().year - 1], data_dir=os.path.join(os.getcwd(), 'data'), image_dir=os.path.join(os.getcwd(), 'images'), **kwargs):
    team_ = team.Team(team_name, data_dir=data_dir)
    game_data = team_.get_game_data(timeline=timeline)
    if (feature == "result" or feature == "seasons") and rolling_average:
        print("No rolling average definition for result and seasons.")
        print("TODO: Add logic and crap so this isn't a thing anymore")
        raise ValueError('feature cannot be result or seasons')

    plt_sizes = utility.plt_sizes(kwargs)
    plt_labels = utility.plt_labels(team_.name, feature)
    
    plt.figure(figsize=plt_sizes["figsize"])

    plt.plot(game_data[feature].tolist(), linewidth=0.35, color="b", label=feature)
    if rolling_average:
        roll = game_data[feature].rolling(window=12)
        plt.plot(roll.mean(), linewidth=1.0, color="r", label="rolling average")

    plt.ylabel(plt_labels['ylabel'], fontsize=plt_sizes["labelsize"])
    plt.xlabel(plt_labels['xlabel'], fontsize=plt_sizes["labelsize"])
    plt.title(plt_labels['title'], fontsize=plt_sizes["titlesize"])
    plt.legend(loc='best', fancybox=True)

    tick_locs = []
    tick_labels = []
    seasons = game_data["seasons"].tolist()
    curr_season = seasons[0]
    for i in range(len(seasons)):
        if curr_season != seasons[i]:
            tick_locs += [i]
            tick_labels += [curr_season]
            curr_season = seasons[i]
    tick_locs += [len(seasons) - 1]
    tick_labels += [seasons[len(seasons) - 1]]
    plt.xticks(tick_locs, tick_labels, rotation=90, fontsize=plt_sizes["ticksize"])
    plt.grid(which='major', axis='x')
    if feature == "point_diff":
        plt.hlines(0, 0, len(game_data))
    plt.tight_layout()

    plt.savefig(os.path.join(image_dir, plt_labels["image"]))

def plot_team_compare(team_A_name, team_B_name, feature, rolling_average = True, timeline=[1880, datetime.now().year - 1],  data_dir=os.path.join(os.getcwd(), 'data'), image_dir=os.path.join(os.getcwd(), 'images'), **kwargs):

    team_A = team.Team(team_A_name, data_dir=data_dir)
    team_B = team.Team(team_B_name, data_dir=data_dir)

    team_A_data = team_A.get_game_data(timeline=timeline)
    team_B_data = team_B.get_game_data(timeline=timeline)
    
    if (feature == "result" or feature == "seasons") and rolling_average:
        print("No rolling average definition for result and seasons.")
        #TODO: Add logic and crap so this isn't a thing anymore
        print("TODO: Add logic and crap so this isn't a thing anymore")
        raise ValueError('feature cannot be result or seasons')

    comparison = [team_A.name, team_B.name]
    comparison.sort()

    plt_sizes = utility.plt_sizes(kwargs)
    plt_labels = utility.plt_labels(' v '.join(comparison), feature)
    
    plt.figure(figsize=plt_sizes["figsize"])

    plt.plot(team_A_data[feature].tolist(), linewidth=0.35, color="purple", label=team_A.name + " " + feature)
    plt.plot(team_B_data[feature].tolist(), linewidth=0.35, color="blue", label=team_B.name + " " + feature)

    if rolling_average:
        roll_A = team_A_data[feature].rolling(window=12)
        plt.plot(roll_A.mean(), linewidth=1.0, color="green", label=team_A.name + " rolling average")
        roll_B = team_B_data[feature].rolling(window=12)
        plt.plot(roll_B.mean(), linewidth=1.0, color="red", label=team_B.name + " rolling average")

    plt.ylabel(plt_labels['ylabel'], fontsize=plt_sizes["labelsize"])
    plt.xlabel(plt_labels['xlabel'], fontsize=plt_sizes["labelsize"])
    plt.title(plt_labels['title'], fontsize=plt_sizes["titlesize"])
    plt.legend(loc='best', fancybox=True)

    tick_locs = []
    tick_labels = []
    if team_A_data["seasons"][0] <= team_B_data["seasons"][0]:
        seasons = team_A_data["seasons"].tolist()
    else:
        seasons = team_B_data["seasons"].tolist()
    curr_season = seasons[0]
    for i in range(len(seasons)):
        if curr_season != seasons[i]:
            tick_locs += [i]
            tick_labels += [curr_season]
            curr_season = seasons[i]
    tick_locs += [len(seasons) - 1]
    tick_labels += [seasons[len(seasons) - 1]]
    plt.xticks(tick_locs, tick_labels, rotation=90, fontsize=plt_sizes["ticksize"])
    plt.grid(which='major', axis='x')
    if feature == "point_diff":
        plt.hlines(0, 0, max([len(team_A_data), len(team_B_data)]))
    plt.tight_layout()

    plt.savefig(os.path.join(image_dir, plt_labels["image"]))
