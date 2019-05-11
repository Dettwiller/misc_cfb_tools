import pandas as pd

def process_game_data(raw_game_df):
    filtered_data = raw_game_df[raw_game_df.away_conference.notnull() & raw_game_df.home_conference.notnull()]
    processed_data = filtered_data.filter(['home_team', 'home_points', 'away_team', 'away_points', 'neutral_site', 'id', 'season'], axis=1)
    diff = []
    total = []
    winner = []
    for row in processed_data.itertuples(name='games'):
        diff += [row.home_points - row.away_points]
        total += [row.home_points + row.away_points]
        if row.home_points > row.away_points:
            winner += [row.home_team]
        else:
            winner += [row.away_team]
    processed_data['point_differential'] = diff
    processed_data['total_points'] = total
    processed_data['winner'] = winner
    return processed_data
    