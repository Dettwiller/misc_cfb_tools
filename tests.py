from os import getcwd
import pandas as pd
from os.path import join
from git_cfb import utility

data_dir = join(getcwd(), "data")

test_csv_filename = "Mississippi State_drive_data_2015-2018.csv"
# print(utility.csv_decomp(test_csv_filename))
# test_subcsv_filename = "Mississippi State_drive_data_2017-2018.csv"
# utility.csv_subdata_search(test_subcsv_filename, data_dir)

test_df = pd.read_csv(join(data_dir, test_csv_filename))
test_new_df = utility.drives_from_recent_games(test_df, last_games=3)
print(test_new_df)
test_new_curr_df = utility.drives_from_recent_games(test_df, last_games=3, curr_game=401012298)
print(test_new_curr_df)
