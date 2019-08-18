from os import getcwd
from os.path import join

if __name__ == '__main__':

    data_dir = join(getcwd(), "data")
    model_timeline = [2008, 2018]
    data_timeline = [2005, 2018]

    # TODO use multiprocessing to download all team game data in parallel
    # TODO use multiprocessing to analyze all games over  model_timeline in parallel
    # TODO calculate useful values like RMSE
    # TODO output results to csv