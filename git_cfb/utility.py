import numpy as np
#TODO: remove __ from all function names
def __plt_sizes(kwargs_dict):
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

def __plt_labels(team_name, feature):
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
    new_df = original_df.filter(like=str(most_recent_games[0]), axis="game_id")
    for i in range(1, last_games):
        new_df.append(original_df.filter(like=str(most_recent_games[i]), axis="game_id"))
    return new_df


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
        #TODO: add logic (may require refactor) to get ppd over seasons, season, and games
        #TODO: add logic to figure out if a game ended or quarter changed for turnover calcs
        #TODO: add game end/quarter logic for drives per game calculations
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
                game == this_game
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
        ppd['offense'] = np.mean(np_offense_results)
        ppd['offense_s'] = np.std(np_offense_results)
        ppd['defense'] = np.mean(np_defense_results)
        ppd['defense_s'] = np.std(np_defense_results)
        ppd['dpg'] = np.mean(np_drives_per_game)
        ppd['dpg_s'] = np.std(np_drives_per_game)
