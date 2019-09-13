from os import getcwd
from football_modeling import fetch_data
import numpy as np

data_dir = getcwd()
downloader = fetch_data.data_downloader(data_dir=data_dir)

msu = downloader.get_recruiting_data("Charlotte", [2016, 2019], 'msu_recruiting.csv', True)
bama = downloader.get_recruiting_data("Alabama", [2016, 2019], 'bama_recruiting.csv', True)

msu_mean = np.mean(msu['points'])
bama_mean = np.mean(bama['points'])

print(msu)
print(msu_mean)

print(bama)
print(bama_mean)

total_points = msu_mean + bama_mean

msu_prop = msu_mean / total_points
bama_prop = bama_mean / total_points
print(msu_prop)
print(bama_prop)

msu_rank = np.mean(msu['rank'])
bama_rank = np.mean(bama['rank'])
total_rank = msu_rank + bama_rank
print(1.0 - msu_rank /total_rank)
print(1.0 - bama_rank / total_rank)