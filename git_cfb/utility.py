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

def ppd_calculation(team_name, drive_tuple, turn_over=False):
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