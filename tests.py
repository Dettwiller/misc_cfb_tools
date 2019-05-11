from os import getcwd
from os.path import join
from git_cfb import utility

data_dir = join(getcwd(), "data")

test_csv_filename = "Mississippi State_drive_data_2015-2018.csv"
print(utility.csv_decomp(test_csv_filename))
test_subcsv_filename = "Mississippi State_drive_data_2017-2018.csv"
utility.csv_subdata_search(test_subcsv_filename, data_dir)