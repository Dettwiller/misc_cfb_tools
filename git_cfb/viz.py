import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

from . import fetch_data, utility


def plot_team_feature(team_name, feature, rolling_average = True, team_data=None, timeline=[1880, datetime.now().year - 1], data_dir = os.getcwd(), image_dir = os.getcwd(), **kwargs):
    if team_data is not None:
        assert(isinstance(team_data, pd.DataFrame))
    else:
        team_data = fetch_data.get_team_data(team_name, timeline=timeline, data_dir=data_dir)
    
    if (feature == "result" or feature == "seasons") and rolling_average:
        print("No rolling average definition for result and seasons.")
        print("TODO: Add logic and crap so this isn't a thing anymore")
        raise ValueError('feature cannot be result or seasons')

    plt_sizes = utility.__plt_sizes(kwargs)
    plt_labels = utility.__plt_labels(team_name, feature)
    
    plt.figure(figsize=plt_sizes["figsize"])

    plt.plot(team_data[feature].tolist(), linewidth=0.35, color="b", label=feature)
    if rolling_average:
        roll = team_data[feature].rolling(window=12)
        plt.plot(roll.mean(), linewidth=1.0, color="r", label="rolling average")

    plt.ylabel(plt_labels['ylabel'], fontsize=plt_sizes["labelsize"])
    plt.xlabel(plt_labels['xlabel'], fontsize=plt_sizes["labelsize"])
    plt.title(plt_labels['title'], fontsize=plt_sizes["titlesize"])
    plt.legend(loc='best', fancybox=True)

    tick_locs = []
    tick_labels = []
    seasons = team_data["seasons"].tolist()
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
        plt.hlines(0, 0, len(team_data))
    plt.tight_layout()

    plt.savefig(os.path.join(image_dir, plt_labels["image"]))

def plot_team_compare(team_A, team_B, feature, rolling_average = True, team_A_data=None, team_B_data=None, timeline=[1880, datetime.now().year - 1], data_dir = os.getcwd(), image_dir = os.getcwd(), **kwargs):
    if team_A_data is not None:
        assert(isinstance(team_A_data, pd.DataFrame))
    else:
        team_A_data = fetch_data.get_team_data(team_A, timeline=timeline, data_dir=data_dir)

    if team_B_data is not None:
        assert(isinstance(team_B_data, pd.DataFrame))
    else:
        team_B_data = fetch_data.get_team_data(team_B, timeline=timeline, data_dir=data_dir)
    
    if (feature == "result" or feature == "seasons") and rolling_average:
        print("No rolling average definition for result and seasons.")
        #TODO: Add logic and crap so this isn't a thing anymore
        print("TODO: Add logic and crap so this isn't a thing anymore")
        raise ValueError('feature cannot be result or seasons')

    comparison = [team_A, team_B]
    comparison.sort()

    plt_sizes = utility.__plt_sizes(kwargs)
    plt_labels = utility.__plt_labels(' v '.join(comparison), feature)
    
    plt.figure(figsize=plt_sizes["figsize"])

    plt.plot(team_A_data[feature].tolist(), linewidth=0.35, color="purple", label=team_A + " " + feature)
    plt.plot(team_B_data[feature].tolist(), linewidth=0.35, color="blue", label=team_B + " " + feature)

    if rolling_average:
        roll_A = team_A_data[feature].rolling(window=12)
        plt.plot(roll_A.mean(), linewidth=1.0, color="green", label=team_A + " rolling average")
        roll_B = team_B_data[feature].rolling(window=12)
        plt.plot(roll_B.mean(), linewidth=1.0, color="red", label=team_B + " rolling average")

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
