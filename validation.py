from os import getcwd
from os.path import join

from football_modeling import model_evaluation, ppd_model, fetch_data

if __name__ == '__main__':

    data_dir = join(getcwd(), "validation_data")
    drives_dir = join(getcwd(), "drives_data")
    games_dir = join(getcwd(), "games_data")
    model_timeline = [2008, 2018]
    data_timeline = [2005, 2018]
    weights = [0.025, 0.125, 0.85]
    ranges = [3, 1, 3]
    hfa = 0.0

    # data_downloader = fetch_data.data_downloader(data_dir=drives_dir)
    fetch_data.parallel_download_all_team_data(data_dir=drives_dir, data_type='drives', timeline=data_timeline, print_progress=True)
    # data_downloader.change_download_directory(games_dir)
    fetch_data.parallel_download_all_team_data(data_dir=games_dir, data_type='games', timeline=model_timeline, print_progress=True)

    model_evaluator = model_evaluation.evaluator(model_timeline, data_timeline, data_dir=data_dir, games_dir=games_dir, modeling_data_dir=drives_dir)
    # model_evaluator.download_game_data(model_timeline, print_progress=True)
    # model_evaluator.download_model_data(data_timeline, data_type='drives', print_progress=True)

    model_ppd = ppd_model.ppd_model(weights, ranges, home_field_advantage=hfa)

    model_evaluator.evaluate_model(model_ppd, model_timeline, data_timeline, data_type='drives', print_progress=True) # TODO finish this function
    # TODO build model_evaluator.parallel_evaluate_model()