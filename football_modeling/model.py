from collections.abc import Iterable

def generic_model(weights, ranges, home_field_advantage=0.0):
    model = Model(weights, ranges, home_field_advantage=home_field_advantage)
    return model

class Model:
    '''
    Class for creating "generic" models
    
    Args:
        ranges: iterable of 3 entries corresoponding to:
                [years of historical data, seasons of recent data, and games of current data]

        weights: iterable of 3 entries corresponding to the weight given to each range:
                [historical, recent, current]

        home_field_advantage: additional points given to the home team
    '''
    def __init__(self, weights, ranges, home_field_advantage=0.0):
        weights_type_check = isinstance(weights, Iterable)
        assert weights_type_check, "weights is not iterable: %r" % weights
        weights_len_check = len(weights) == 3
        assert weights_len_check, "weights does not contain 3 entries: %r" % weights
        weights_sum_check = abs(sum(weights) - 1.0) < 1e-8
        assert weights_sum_check, "weights do not sum to 1+-1e-8: %r" % weights_sum_check
        weights_sign_check = all([weight >= 0.0 for weight in weights])
        assert weights_sign_check, "weights are not all >= 0.0: %r" % weights

        ranges_type_check = isinstance(ranges, Iterable)
        assert ranges_type_check, "ranges is not iterable: %r" % ranges
        ranges_len_check = len(ranges) == 3
        assert ranges_len_check, "ranges does not contain 3 entries: %r" % ranges
        ranges_sign_check = all([range_ >= 0.0 for range_ in ranges])
        assert ranges_sign_check, "ranges are not all >= 0.0: %r" % ranges

        home_field_type_check = isinstance(home_field_advantage, float)
        assert home_field_type_check, "home_field_advantage is not a float: %r" % type(home_field_advantage)

        self.home_field_advantage = home_field_advantage
        self.weights = weights
        self.ranges = ranges

    def _get_current_season(self, data_df, timeline, predicted_game_id):
        seasons = []
        for i in range(timeline[0], timeline[1] + 1):
            seasons += [i]
        if predicted_game_id:
            if predicted_game_id in data_df["game_id"].values:
                i_predicted_game_first_drive = data_df[data_df["game_id"] == predicted_game_id].index[0]
            else:
                previous_game_id = 0
                for game_id in data_df["game_id"].values:
                    if int(game_id) > previous_game_id and int(game_id) < predicted_game_id:
                        previous_game_id = int(game_id)
                i_predicted_game_first_drive = data_df[data_df['game_id'] == previous_game_id].index[0]
            current_season = int(data_df["season"].iloc[i_predicted_game_first_drive])
        else:
            current_season = seasons[-1]
        return current_season

    def _get_historical_data(self, current_season, data_df):
        hist_seasons = [current_season - i for i in range(1, 1+self.ranges[0])]
        hist_data = data_df.loc[data_df['season'].isin(hist_seasons)]
        return hist_data
    
    def _get_recent_data(self, current_season, data_df):
        recent_data = data_df.loc[data_df['season'] == current_season]
        if recent_data.empty: # TODO: if the current season contains less than self.ranges[2] games
            current_season -=1
            recent_data = data_df.loc[data_df['season'] == current_season]
        return recent_data

    def _get_current_data(self, data_df, predicted_game_id):
        if predicted_game_id:
            if predicted_game_id in data_df['game_id'].values:
                i_predicted_game = data_df.loc[(data_df['game_id'] == predicted_game_id)].index[-1]
                i_offset = 1
            else:
                previous_game_id = 0
                for game_id in data_df["game_id"].values:
                    if int(game_id) > previous_game_id and int(game_id) < predicted_game_id:
                        previous_game_id = int(game_id)
                i_predicted_game = data_df.loc[(data_df["game_id"] == previous_game_id)].index[-1]
                i_offset = 0
            searching = True
            while searching:
                candidate_game = data_df['game_id'].iloc[i_predicted_game - i_offset]
                if candidate_game != predicted_game_id:
                    previous_game_id = candidate_game
                    searching = False
                i_offset += 1
        else:
            previous_game_id = data_df['game_id'].iloc[-1]
        most_recent_games = [previous_game_id]
        i_previous_game = data_df.loc[(data_df['game_id'] == previous_game_id)].index[-1]
        i = 0
        while len(most_recent_games) < self.ranges[2] and i < len(data_df):
            candidate_game = data_df['game_id'].iloc[i_previous_game - i]
            if candidate_game != most_recent_games[-1]:
                most_recent_games += [candidate_game]
            i += 1
        current_data = data_df.loc[data_df['game_id'].isin(most_recent_games)]
        return current_data