import os
from datetime import datetime

import numpy as np
import pandas as pd
import requests

# * Team example
# r = requests.get('https://api.collegefootballdata.com/games?year=2018&team=Mississippi State')
# r = requests.get('https://api.collegefootballdata.com/games?year=' + str(start) + '&team=Mississippi State')

# * Conference example
# website = 'https://api.collegefootballdata.com/games?year=' + str(start) + '&conference=SEC'

def download_SEC_data(timeline=[1880, datetime.now().year - 1], save=True):
    website = 'https://api.collegefootballdata.com/games?year=' + str(timeline[0]) + '&conference=SEC'
    r = requests.get(website)
    x = r.json()
    total_df = pd.DataFrame(x)
    for i in range(timeline[0] + 1, timeline[1] + 1):
        year = str(i)
        print(year)
        website = 'https://api.collegefootballdata.com/games?year=' + year + '&conference=SEC'
        r = requests.get(website)
        x = r.json()
        new_df = pd.DataFrame(x)
        if not new_df.empty:
            total_df = total_df.append(new_df, ignore_index = True) 
    if save:
        total_df.to_csv("sec_all_history.csv")
    return total_df

def download_team_data(team_name, timeline=[1880, datetime.now().year - 1], data_dir = os.getcwd()):
    website = 'https://api.collegefootballdata.com/games?year=' + str(timeline[0]) + '&team=' + team_name
    r = requests.get(website)
    x = r.json()
    total_df = pd.DataFrame(x)
    for i in range(timeline[0] + 1, timeline[1] + 1):
        year = str(i)
        print(year)
        website = 'https://api.collegefootballdata.com/games?year=' + year + '&team=' + team_name
        r = requests.get(website)
        x = r.json()
        new_df = pd.DataFrame(x)
        if not new_df.empty:
            total_df = total_df.append(new_df, ignore_index = True) 
    total_df.to_csv(os.path.join(data_dir,team_name + "_all_history.csv"))
    return total_df

def get_team_data(team_name, timeline=[1880, datetime.now().year - 1], data_dir = os.getcwd()):
    if os.path.isfile(os.path.join(data_dir, team_name + "_all_history.csv")):
        total_df = pd.read_csv(os.path.join(data_dir, team_name + "_all_history.csv"))
    else:
        total_df = download_team_data(team_name, timeline=timeline, data_dir=data_dir)

    away_games = total_df.index[total_df['away_team'] == team_name]
    home_games = total_df.index[total_df['home_team'] == team_name]
    games_list = away_games.tolist() + home_games.tolist()
    games_list.sort()

    games = pd.Index(games_list)
    games_df = total_df.loc[games]

    points_scored = []
    points_allowed = []
    point_diff = []
    result = []
    seasons = []
    for row in games_df.itertuples(name='game'):
        if row.away_team == team_name:
            points_scored += [row.away_points]
            points_allowed +=[row.home_points]
            point_diff += [row.away_points - row.home_points]
        else:
            points_scored += [row.home_points]
            points_allowed +=[row.away_points]
            point_diff += [row.home_points - row.away_points]
        if point_diff[-1] > 0:
            result += [1]
        else:
            result += [0]
        seasons += [row.season]
    team_data = pd.DataFrame(data={'seasons': seasons, 'points_scored': points_scored, 
                                    'points_allowed': points_allowed, 'point_diff': point_diff, 'result': result})
    return team_data
