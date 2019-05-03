import numpy as np
from scipy.stats import norm
# import matplotlib.pyplot as plt

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


def drive_scoring(team_name, drive_tuple, turn_over=False):
    '''
        Consider asking for the next drives results for any change of 
        possession event, not just INT and FUMBLE
    '''
    drive_result = getattr(drive_tuple, "drive_result")
    if drive_result == "TD":
        return 7, getattr(drive_tuple, "offense") == team_name
    elif drive_result == "FG":
        return 3, getattr(drive_tuple, "offense") == team_name
    elif drive_result == "PUNT" or drive_result == "DOWNS" or turn_over:
        return 0, getattr(drive_tuple, "offense") == team_name
    else:
        return drive_result, getattr(drive_tuple, "offense") == team_name

def calculate_ppd(name, drives_df):
    #TODO: add logic to figure out if a game ended or quarter changed for turnover calcs
    turn_over = False
    offense_results = []
    defense_results = []
    drives_per_game = []
    game_drives = 0
    game = -1
    for drive in drives_df.itertuples(index=True, name='Drive'):
        this_game = getattr(drive, "game_id")
        if game == this_game:
            game_drives += 1
        else:
            drives_per_game +=[game_drives]
            game = this_game
            game_drives = 1
        drive_points, on_offense = drive_scoring(name, drive, turn_over=turn_over)
        if type(drive_points) == str:
            turn_over = True

        elif on_offense and not turn_over:
            offense_results += [drive_points]
            turn_over = False

        elif not on_offense and not turn_over:
            defense_results += [drive_points]
            turn_over = False

        elif not on_offense and turn_over:
            offense_results += [-1 * drive_points]
            defense_results += [drive_points]
            turn_over = False

        elif on_offense and turn_over:
            defense_results += [-1 * drive_points]
            offense_results += [drive_points]
            turn_over = False

    np_offense_results = np.array(offense_results)
    np_defense_results = np.array(defense_results)
    np_drives_per_game = np.array(drives_per_game)

    ppd = {}
    ppd['offense'] = (np.mean(np_offense_results), np.var(np_offense_results))
    ppd['defense'] = (np.mean(np_defense_results), np.var(np_defense_results))
    ppd['dpg'] = (np.mean(np_drives_per_game), np.var(np_drives_per_game))

    return ppd

def disc_to_dist(x, f, delta):
    mean = (x * f).sum() * delta
    var = ((x ** 2.0) * f).sum() * delta - mean ** 2.0
    return (mean, var)

def dist_mult(dist_A, dist_B, sigma_range=6, res=10000):
    left_side = min([dist_A[0] - 6 * dist_A[1], dist_B[0] - 6 * dist_B[1]])
    right_side = max([dist_A[0] + 6 * dist_A[1], dist_B[0] + 6 * dist_B[1]]) 

    x = np.linspace(left_side, right_side, res)
    # * for reference and f_A/f_B checking, do not delete
    # * delta = (right_side - left_side) / res 

    f_A = norm.pdf(x, dist_A[0], np.sqrt(dist_A[1]))
    f_B = norm.pdf(x, dist_B[0], np.sqrt(dist_B[1]))

    disc_result = (f_A * f_B) / (f_A * f_B).sum()
    dist_result = disc_to_dist(x, disc_result, 1.0) # * the result is already normalized, so delta = 1.0

    return dist_result

def pred_score(team_A_ppd_dists, team_B_ppd_dists):
    # * Rules for normal distributions
    # * N(m1, v1) + N(m2, v2) = N(m1 + m2, v1 + v2)
    # * N(m1, v1) - N(m2, v2) = N(m1 - m2, v1 - v2)
    # * a*N(m1, v1) = N( a*m1, (a^2)*v1 ) 

    pred_team_A_ppd = ( (team_A_ppd_dists['offense'][0] + team_B_ppd_dists['defense'][0]) / 2.0, 
                             (team_A_ppd_dists['offense'][1] + team_B_ppd_dists['defense'][1]) / 4.0 )
    
    pred_team_B_ppd = ( (team_B_ppd_dists['offense'][0] + team_A_ppd_dists['defense'][0]) / 2.0, 
                             (team_B_ppd_dists['offense'][1] + team_A_ppd_dists['defense'][1]) / 4.0 )

    pred_dpg = ( (team_A_ppd_dists['dpg'][0] + team_B_ppd_dists['dpg'][0]) / 2.0, 
                             (team_A_ppd_dists['dpg'][1] + team_B_ppd_dists['dpg'][1]) / 4.0 )

    pred_team_A_score = dist_mult(pred_team_A_ppd, pred_dpg)
    pred_team_B_score = dist_mult(pred_team_B_ppd, pred_dpg)

    return pred_team_A_score, pred_team_B_score

def ppd_kwargs_filter(kwargs_dict):
    ppd_args_dict = {}
    if 'weights' in kwargs_dict:
        ppd_args_dict['weights'] = kwargs_dict['weights']
    else:
        ppd_args_dict['weights'] = [0.15, 0.35, 0.5]
    if 'home_field' in kwargs_dict:
        ppd_args_dict['home_field'] = kwargs_dict['home_field']
    else:
        ppd_args_dict['home_field'] = 3.0

    return ppd_args_dict
