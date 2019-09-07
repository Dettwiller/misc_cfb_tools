from collections import namedtuple
from collections.abc import Iterable
from csv import reader, writer
from os import listdir
from os.path import exists, isfile, join, splitext
from datetime import datetime

import numpy as np
import requests
from scipy.stats import norm

import json

def directory_check(directory):
    directory_file_check = isfile(directory)
    directory_exist_check = exists(directory)
    directory_error_statement = "directory does not exist: %r" % directory
    assert directory_exist_check and not directory_file_check, directory_error_statement

def file_check(filename, directory=False):
    filename_type_check = isinstance(filename, str)
    assert filename_type_check, "filename is not string: %r" % type(filename)
    if directory:
        directory_check(directory)
        file_path = join(directory, filename)
        file_exist_check = exists(file_path)
        assert file_exist_check, "directory indicates to check for file and file does not exist: %r" % file_path

def website_check(url):
    url_type_check = isinstance(url, str)
    assert url_type_check, "url is not a string: %r" % type(url)
    website_content = requests.get(url)
    website_request_check = website_content.status_code == 200
    assert website_request_check, "broken link or website is down"
    return website_content

def timeline_check(timeline):
    timeline_type_check = isinstance(timeline, Iterable)
    assert timeline_type_check, "timeline is not iterable: %r" % timeline
    timeline_len_check = len(timeline) == 2
    assert timeline_len_check, "timeline does not contain two elements: %r" % timeline
    timeline_value_check = timeline[1] >= timeline[0]
    assert timeline_value_check, "timeline is not ordered [lower, upper]: %r" % timeline

def csv_decomposer(csv_filename):
    file_check(csv_filename)

    csv_filename_split_list = csv_filename.split("_")
    start_year = int(csv_filename_split_list[-1].split("-")[0])
    end_year = int(csv_filename_split_list[-1].split("-")[-1].split(".")[0])
    timeline = [start_year, end_year]
    base_name = '_'.join(csv_filename_split_list[:-1])
    return base_name, timeline

def create_sub_csv(new_csv_filename, timeline, source_csv_filename, data_dir):
    file_check(new_csv_filename)
    timeline_check(timeline)
    directory_check(data_dir)
    file_check(source_csv_filename, data_dir)

    new_csv = join(data_dir, new_csv_filename)
    source_csv = join(data_dir, source_csv_filename)
    with open(source_csv, "r", encoding='utf-8', errors='ignore') as scsv:
        with open(new_csv, "w+", newline='', encoding='utf-8') as ncsv:
            source_reader = reader(scsv, delimiter=',')
            writer_obj = writer(ncsv, delimiter=',')
            header = next(source_reader, None)
            writer_obj.writerow(header)
            season_index = header.index('season') # * all .csv datafiles should be tagged by season
            line = next(source_reader, False)
            while line:
                season = int(line[season_index])
                if season >= timeline[0] and season <= timeline[1]:
                    writer_obj.writerow(line)
                line = next(source_reader, False)

def csv_subdata_search(csv_filename, data_dir):
    file_check(csv_filename)
    directory_check(data_dir)

    base_name, desired_timeline = csv_decomposer(csv_filename)
    data_dir_contents = iter(listdir(data_dir))
    searching = True
    while searching:
        item = next(data_dir_contents, False)
        if not item:
            searching = False
        elif item == csv_filename:
            searching = False
        else:
            pathed_item = join(data_dir, item)
            _, extension = splitext(pathed_item)
            if isfile(pathed_item) and extension == '.csv':
                candidate_base_name, candidate_timeline = csv_decomposer(item)
                name_match = candidate_base_name == base_name
                left_year = candidate_timeline[0] <= desired_timeline[0]
                right_year = candidate_timeline[1] >= desired_timeline[1]
                if name_match and left_year and right_year:
                    create_sub_csv(csv_filename, desired_timeline, pathed_item, data_dir)
                    searching = False

def weighted_average_gaussian_distributions(distributions, weights):
    distributions_type_check = isinstance(distributions, Iterable)
    assert distributions_type_check, "distributions is not iterable: %r" % distributions
    distribution_type_check = all([isinstance(distribution, Iterable) for distribution in distributions])
    assert distribution_type_check, "all distributions in distributions are not iterable: %r" % distributions
    distribution_len_check = all([len(distribution) == 2 for distribution in distributions])
    assert distribution_len_check, "all distributions in distributions are not len = 2 (mean, var): %r" % distributions
    variance_list = [distribution[1] for distribution in distributions]
    variance_check = all([variance > 0 for variance in variance_list]) # probably should be > 0.0
    assert variance_check, "all variances are not > 0: %r" % variance_list
    weights_type_check = isinstance(weights, Iterable)
    assert weights_type_check, "weights is not iterable: %r" % weights
    weights_distribution_len_check = len(distributions) == len(weights)
    assert weights_distribution_len_check, "weights and distributions are not the same length"

    mean_list = [distribution[0] for distribution in distributions]
    mean_average_distribution = 0.0
    variance_average_distribution = 0.0
    for i in range(len(mean_list)):
        mean_average_distribution += weights[i] * mean_list[i]
        variance_average_distribution += weights[i] ** 2.0 * variance_list[i]
    mean_average_distribution = mean_average_distribution / sum(weights)
    variance_average_distribution = variance_average_distribution / (sum(weights) ** 2)
    return (mean_average_distribution, variance_average_distribution)

def average_gaussian_distributions(distributions):
    distributions_type_check = isinstance(distributions, Iterable)
    assert distributions_type_check, "distributions is not iterable: %r" % distributions
    distribution_type_check = all([isinstance(distribution, Iterable) for distribution in distributions])
    assert distribution_type_check, "all distributions in distributions are not iterable: %r" % distributions
    distribution_len_check = all([len(distribution) == 2 for distribution in distributions])
    assert distribution_len_check, "all distributions in distributions are not len = 2 (mean, var): %r" % distributions
    variance_list = [distribution[1] for distribution in distributions]
    variance_check = all([variance > 0 for variance in variance_list])
    assert variance_check, "all variances are not > 0: %r" % variance_list

    n_distributions = len(distributions)
    mean_list = [distribution[0] for distribution in distributions]

    mean_average_distribution = sum(mean_list) / n_distributions
    variance_average_distribution = sum(variance_list) / (n_distributions ** 2)
    return (mean_average_distribution, variance_average_distribution)

def multiply_gaussians(d_a, d_b, n_samples=int(1e6)):
    d_a_type_check = isinstance(d_a, Iterable)
    assert d_a_type_check, "first distribution is not iterable: %r" % d_a
    d_a_len_check = len(d_a) == 2
    assert d_a_len_check, "first distribution does not have 2 entries (mean, variance): %r" % d_a
    d_a_var_check = d_a[1] > 0
    assert d_a_var_check, "first distribtution variance is not > 0: %r" % d_a[1]

    d_b_type_check = isinstance(d_b, Iterable)
    assert d_b_type_check, "second distribution is not iterable: %r" % d_b
    d_b_len_check = len(d_b) == 2
    assert d_b_len_check, "second distribution does not have 2 entries (mean, variance): %r" % d_b
    d_b_var_check = d_b[1] > 0
    assert d_b_var_check, "second distribtution variance is not > 0: %r" % d_b[1]

    n_samples_type_check = isinstance(n_samples, int)
    assert n_samples_type_check, "n_samples is not integer: %r" % type(n_samples)
    n_samples_value_check = n_samples > 0
    assert n_samples_value_check, "n_samples is not > 0: %r" % n_samples

    sample_a = norm.rvs(d_a[0], np.sqrt(d_a[1]), size=n_samples)
    sample_b = norm.rvs(d_b[0], np.sqrt(d_b[1]), size=n_samples)
    sample_ab = sample_a * sample_b
    mean_ab = np.mean(sample_ab)
    var_ab = np.var(sample_ab)
    assert var_ab > 0, "combined sample variance is not > 0: %r" % var_ab
    result = (mean_ab, var_ab)
    return result

def new_fbs_schools_check(game_tuple):
    # TODO isinstance game_tuple
    new_teams = {
        "Georgia State": 2014, "Georgia Southern": 2015,
        "Appalachian State": 2015, "Coastal Carolina": 2018,
        "UAB": 2018, "Liberty": 2018, "UMass": 2013,
        "Charlotte": 2016, "Old Dominion": 2015,
        "Texas State": 2013, "South Alabama": 2013,
        "UT San Antonio": 2013, "Western Kentucky": 2010
        }
    valid_game = True
    if game_tuple.home_team in new_teams.keys():
        if int(game_tuple.season) < new_teams[game_tuple.home_team]:
            valid_game = False
    if game_tuple.away_team in new_teams.keys():
        if int(game_tuple.season) < new_teams[game_tuple.away_team]:
            valid_game = False
    return valid_game

def bovada_names_translator(team_name):
    # TODO isinstance string
    translator_bovada_cfb_data = {
        'Miami Florida': 'Miami',
        'Hawaii': "Hawai'i",
        'Massachusetts': 'UMass',
        'Mississippi': 'Ole Miss',
        'Louisiana-Lafayette': 'Louisiana',
        'Miami Ohio': 'Miami (OH)',
        'Middle Tennessee State': 'Middle Tennessee',
        "Cincinnati U": "Cincinnati",
        "South Florida Bulls": "South Florida",
        "Texas-San Antonio": "UT San Antonio",
        "UL Monroe": "Louisiana Monroe",
        "Central Florida": "UCF",
        "Buffalo U": "Buffalo",
        "San Jose State": "San José State",
        "Washington U": "Washington"
    }
    if team_name in translator_bovada_cfb_data.keys():
        cfb_data_team_name = translator_bovada_cfb_data[team_name]
    else:
        cfb_data_team_name = team_name
    # print(team_name + " translated to " + cfb_data_team_name)
    return cfb_data_team_name

def _bovada_team_names(bovada_event):
    home_teamname = ""
    away_teamname = ""
    bovada_home_team_name = ""
    bovada_away_team_name = ""
    for team in bovada_event['competitors']:
        if team["home"]:
            bovada_home_team_name = team["name"].split('#')[0].strip()
            home_teamname = bovada_names_translator(bovada_home_team_name)
            if not home_teamname:
                print("home team name error: " + str(team["name"]) + ", type = " + str(type(team["name"])))
                print(bovada_home_team_name)
        elif not team["home"]:
            bovada_away_team_name = team["name"].split('#')[0].strip()
            away_teamname = bovada_names_translator(bovada_away_team_name)
            if not away_teamname:
                print("away team name error: " + str(team["name"]) + ", type = " + str(type(team["name"])))
                print(bovada_away_team_name)
        else:
            print("home team bool error: team['home'] = " + str(team["home"]) + ", type = " + str(type(team['home'])))
    return away_teamname, home_teamname, bovada_home_team_name, bovada_away_team_name

def _bovada_odds_team_names(bovada_team_name):
    problem_names = {
        # "Michigan State": "Michigan ST Spartans"
    } # Apparently this is only sometimes a problem
    if bovada_team_name in problem_names.keys():
        bovada_odds_team_name = problem_names[bovada_team_name]
    else:
        bovada_odds_team_name = bovada_team_name
    return bovada_odds_team_name

def get_cfb_odds(fbs_team_list):
    # TODO: input checking
    Matchup = namedtuple('Matchup', 'date neutral_site away_team home_team home_spread away_spread_odds home_spread_odds away_win_odds home_win_odds total over_odds under_odds')
    try:
        source = requests.get("https://www.bovada.lv/services/sports/event/v2/events/A/description/football/college-football").json()
    except:
        raise ConnectionError("url is likely not responding")
    with open("odds_data.txt", "w+", encoding='utf-8', errors='ignore') as eodf:
        eodf.write(json.dumps(source, indent=4, sort_keys=True))

    games = []
    for event in source[0]['events']:
        away_teamname, home_teamname, bovada_home_team_name, bovada_away_team_name = _bovada_team_names(event)
        bovada_odds_home_team_name = _bovada_odds_team_names(bovada_home_team_name)
        bovada_odds_away_team_name = _bovada_odds_team_names(bovada_away_team_name)
        
        if home_teamname in fbs_team_list and away_teamname in fbs_team_list:
            # print("success! " + away_teamname + " @ " + home_teamname)
            date = datetime.fromtimestamp(event['startTime'] / 1e3)
            for line in event["displayGroups"][0]['markets']:
                if line['description'] == 'Moneyline' and line['period']['description'] == 'Match':
                    for moneyline_outcome in line['outcomes']:
                        if moneyline_outcome['description'].strip().split("#")[0].strip() == bovada_odds_home_team_name:
                            if moneyline_outcome["price"]["american"] == 'EVEN':
                                home_win_odds = 100
                            else:
                                home_win_odds = int(moneyline_outcome["price"]["american"])
                        elif moneyline_outcome['description'].strip().split("#")[0].strip() == bovada_odds_away_team_name:
                            if moneyline_outcome["price"]["american"] == 'EVEN':
                                away_win_odds = 100
                            else:
                                away_win_odds = int(moneyline_outcome["price"]["american"])
                        else:
                            print("moneyline error: " + moneyline_outcome['description'].strip().split("#")[0].strip())
                            print(bovada_odds_home_team_name)
                            print(bovada_odds_away_team_name)
                            print("moneyline error: " + str(moneyline_outcome['description']) + " " + str(type(moneyline_outcome['description'])))
                elif line['description'] == 'Point Spread' and line['period']['description'] == 'Match':
                    neutral_site = bool(line['notes'])
                    for spread_outcome in line['outcomes']:
                        if spread_outcome['description'].strip().split("#")[0].strip() == bovada_odds_home_team_name:
                            if spread_outcome["price"]["american"] == 'EVEN':
                                home_spread_odds = 100
                            else:
                                home_spread_odds = int(spread_outcome["price"]["american"])
                            home_spread = float(spread_outcome["price"]["handicap"])
                        elif spread_outcome['description'].strip().split("#")[0].strip() == bovada_odds_away_team_name:
                            if spread_outcome["price"]["american"] == 'EVEN':
                                away_spread_odds = 100
                            else:
                                away_spread_odds = int(spread_outcome["price"]["american"])
                        else:
                            print("point spread error: " + str(spread_outcome['description']) + " " + str(type(spread_outcome['description'])))
                elif line['description'] == 'Total' and line['period']['description'] == 'Match':
                    for total_outcome in line['outcomes']:
                        if total_outcome['description'] == "Over":
                            over_odds = int(total_outcome["price"]["american"])
                            total = float(total_outcome["price"]["handicap"])
                        elif total_outcome['description'] == "Under":
                            under_odds = int(total_outcome["price"]["american"])
                        else:
                            print("total error: " + str(total_outcome['description']) + " " + str(type(total_outcome['description'])))
            games += [Matchup(date, neutral_site, away_teamname, home_teamname, home_spread, away_spread_odds, home_spread_odds, away_win_odds, home_win_odds, total, over_odds, under_odds)]
        elif event['competitors']:
            if home_teamname not in fbs_team_list:
                print(home_teamname + " not in fbs_team_list")
            if away_teamname not in fbs_team_list:
                print(away_teamname + " not in fbs_team_list")
        # else:
        #     print('competitors error: ' + str(event['competitors']) + " " + str(type(event['competitors'])))

    return games
