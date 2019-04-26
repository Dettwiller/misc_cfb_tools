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