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

def recent_games(original_df, last_games=3):
    #TODO: get the last 3 game ID's by looping backwards
    #TODO: filter the dataframe for those games
    most_recent_games = [original_df["game_id"].iloc[-1]]
    while len(most_recent_games) < last_games:
        for i in range(2, len(original_df)):
            candidate_game = original_df["game_id"].iloc[-i]
            if candidate_game != most_recent_games[-1]:
                most_recent_games += [candidate_game]
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
    s_A = norm.rvs(dist_A[0], np.sqrt(dist_A[1]), size=ns)
    s_B = norm.rvs(dist_B[0], np.sqrt(dist_B[1]), size=ns)
    s_F = s_A * s_B
    result = (np.mean(s_F), np.var(s_F))
    return result


