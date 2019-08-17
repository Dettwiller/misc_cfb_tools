from os import listdir
from os.path import isfile, join, splitext
import csv
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

    # print("red ppd~N( " + str(dist_A[0]) + ", " + str(dist_A[1]) + " )")
    # print("blue dpg~N( " + str(dist_B[0]) + ", " + str(dist_B[1]) + " )")
    # print("green score~N( " + str(dist_result[0]) + ", " + str(dist_result[1]) + " )")

    # plt.figure("Distribution")
    # plt.plot(x, f_A * delta, color="r")
    # plt.plot(x, f_B * delta, color="b")
    # plt.plot(x, disc_result, color="g")
    # plt.ylabel("f")
    # plt.xlabel("x")
    # plt.show()

def csv_decomp(csv_filename):
    csv_filename_split_list = csv_filename.split("_")
    start_year = int(csv_filename_split_list[-1].split("-")[0])
    end_year = int(csv_filename_split_list[-1].split("-")[-1].split(".")[0])
    timeline = [start_year, end_year]
    base_name = '_'.join(csv_filename_split_list[:-1])
    return base_name, timeline

def create_sub_csv(new_csv_filename, timeline, source_csv_file, data_dir):
    new_csv = join(data_dir, new_csv_filename)
    # output_string = ''
    scsv = open(source_csv_file, 'r')
    ncsv = open(new_csv, 'w+',  newline='')
    source_reader = csv.reader(scsv, delimiter=',')
    writer = csv.writer(ncsv, delimiter=',')
    header = next(source_reader, None)
    writer.writerow(header)
    season_index = header.index('season') # * all .csv datafiles should be tagged by season
    line = next(source_reader, False)
    while line:
        season = int(line[season_index])
        if season >= timeline[0] and season <= timeline[1]:
            writer.writerow(line)
        line = next(source_reader, False)

def csv_subdata_search(csv_filename, data_dir):
    base_name, desired_timeline = csv_decomp(csv_filename)
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
                candidate_base_name, candidate_timeline = csv_decomp(item)
                name_match = candidate_base_name == base_name
                left_year = candidate_timeline[0] <= desired_timeline[0]
                right_year = candidate_timeline[1] >= desired_timeline[1]
                if name_match and left_year and right_year:
                    create_sub_csv(csv_filename, desired_timeline, pathed_item, data_dir)
                    searching = False

def plt_sizes(kwargs_dict):
    plt_sizes = {'labelsize': 10, 'titlesize': 12, 'ticksize': 8, 'figsize': (6.4, 4.8)}
    if "labelsize" in kwargs_dict:
        plt_sizes["labelsize"] = kwargs_dict["labelsize"]

    if "titlesize" in kwargs_dict:
        plt_sizes["titlesize"] = kwargs_dict["titlesize"]

    if "ticksize" in kwargs_dict:
        plt_sizes["ticksize"] = kwargs_dict["ticksize"]

    if "figsize" in kwargs_dict:
        plt_sizes["figsize"] = kwargs_dict["figsize"]

    return plt_sizes

def plt_labels(team_name, feature):
    plt_labels = {}
    if feature == "points_scored":
        plt_labels["ylabel"] = "Points Scored"
        plt_labels["xlabel"] = "Game/Season"
        plt_labels["title"] = team_name + ' Offensive Production, Historical'
        plt_labels["image"] = team_name + "_offensive_prod.png"
    elif feature == "points_allowed":
        plt_labels["ylabel"] = "Points Allowed"
        plt_labels["xlabel"] = "Game/Season"
        plt_labels["title"] = team_name + ' Defensive Production, Historical'
        plt_labels["image"] = team_name + "_defensive_prod.png"
    elif feature == "point_diff":
        plt_labels["ylabel"] = "Point Differential"
        plt_labels["xlabel"] = "Game/Season"
        plt_labels["title"] = team_name + ' Point Differential, Historical'
        plt_labels["image"] = team_name + "_point_diff.png"
    return plt_labels

def drives_from_recent_games(original_df, last_games=3, predicted_game=None):
    if predicted_game:
        if predicted_game in original_df["game_id"].values:
            df_index_predicted = original_df.loc[(original_df["game_id"] == predicted_game)].index[-1]
            i = 1
        else:
            previous_game = 0
            for game_id in original_df["game_id"].values:
                if int(game_id) > previous_game and int(game_id) < predicted_game:
                    previous_game = int(game_id)
            df_index_predicted = original_df.loc[(original_df["game_id"] == previous_game)].index[-1]
            i = 0
        searching = True
        while searching:
            candidate_game = original_df["game_id"].iloc[df_index_predicted - i]
            if candidate_game != predicted_game:
                prev_game = candidate_game
                searching = False
            i += 1
        most_recent_games = [prev_game]
        df_index = original_df.loc[(original_df["game_id"] == prev_game)].index[-1]
    else:
        prev_game = original_df["game_id"].iloc[-1]
        most_recent_games = [prev_game]
        df_index = original_df.loc[(original_df["game_id"] == prev_game)].index[-1]
    # print(original_df[df_index])
    i = 1
    while len(most_recent_games) < last_games and i < len(original_df):
        candidate_game = original_df["game_id"].iloc[df_index - i]
        if candidate_game != most_recent_games[-1]:
            most_recent_games += [candidate_game]
        i += 1
    recent_game_data = original_df.loc[original_df['game_id'].isin(most_recent_games)]

    return recent_game_data

def disc_to_dist(x, f, delta):
    # * outdated, kept for reference ifn
    mean = (x * f).sum() * delta
    var = ((x ** 2.0) * f).sum() * delta - mean ** 2.0
    return (mean, var)

def dist_norm_mult(dist_A, dist_B):
    # * outdated, sample gives better results
    mu = (dist_A[0] * dist_B[1] + dist_B[0] * dist_A[1]) / (dist_A[1] + dist_B[1])
    var = dist_A[1] * dist_B[1] / (dist_A[1] + dist_B[1])

    result = (mu, var)
    return result

def dist_sample_mult(dist_A, dist_B, ns=50000):
    if dist_A[1] <= 0 or dist_B[1] <= 0:
        return (0, 1)
    try:
        s_A = norm.rvs(dist_A[0], np.sqrt(dist_A[1]), size=ns)
    except ValueError:
        print(dist_A)
        return (0, 1)
    try:
        s_B = norm.rvs(dist_B[0], np.sqrt(dist_B[1]), size=ns)
    except ValueError:
        print(dist_B)
        return (0, 1)
    s_F = s_A * s_B
    result = (np.mean(s_F), np.var(s_F))
    return result


