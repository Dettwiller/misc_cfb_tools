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

def download_team_data(team_name, csv_filename, data='games', timeline=[1880, datetime.now().year - 1], data_dir = os.getcwd()):
    # TODO: check the string "data" for 'games' or 'drives' and disallow all other options
    website = 'https://api.collegefootballdata.com/' + data + '?year=' + str(timeline[0]) + '&team=' + team_name
    r = requests.get(website)
    x = r.json()
    total_df = pd.DataFrame(x)
    if data == 'drives':
        total_df['season'] = str(timeline[0])
    for i in range(timeline[0] + 1, timeline[1] + 1):
        year = str(i)
        print(year)
        website = 'https://api.collegefootballdata.com/' + data + '?year=' + year + '&team=' + team_name
        r = requests.get(website)
        x = r.json()
        new_df = pd.DataFrame(x)
        if data == 'drives':
            new_df['season'] = year
        if not new_df.empty:
            total_df = total_df.append(new_df, ignore_index = True) 
    total_df.to_csv(os.path.join(data_dir, csv_filename))
    return total_df

def get_team_data(team_name, data='games', timeline=[1880, datetime.now().year - 1], data_dir = os.getcwd()):
    #TODO: look for any file that has the data in the timeline requested
    #TODO: isolate specific ranges from the file into the dataframe
    # TODO: check the string "data" for 'games' or 'drives' and disallow all other options
    csv_filename = team_name + "_" + data + "_data_" + str(timeline[0]) + "-" + str(timeline[1]) + ".csv"
    if os.path.isfile(os.path.join(data_dir, csv_filename)):
        total_df = pd.read_csv(os.path.join(data_dir, csv_filename))
    else:
        total_df = download_team_data(team_name, csv_filename, data=data, timeline=timeline, data_dir=data_dir)
    
    return total_df