import os
import numpy as np
from git_cfb import fetch_data, model_analysis, model, matchup, team
from multiprocessing import Pool, cpu_count

'''
    TODO: determine the scope of the validation effort:
        * 1. what teams will be involved?
        * 2. what years will be involved?
    TODO: Automate validation
        * 1. get model data for the scope of validation
        * 2. get validation (game) data for the scope of validation
        * 3. predict each game
        *     a. differential
        *     b. total
        *     c. home score
        *     d. away score
            e. home score variance (for minimization in later optimizations)
            f. away score variance (for minimization in later optimizations)
        4. Analyze
            a. RMSE values
                i. differential
                ii. total
                iii. home score
                iv. away score
        5. error table for predicted winner
        6. winner probability? (may want to maximize this in later optimizations)
    TODO: Tune the model
        1. set up optimization
        2. maximize % correct winners?
        3. maximize probability of correct winner
        4. minimize standard deviation of predicted scores
        5. drive differential and total probabilities to 0.5 (accuracy)
        6. multiobjective of 5 and 4
'''

def validation_func(games_df):
    data_dir = os.path.join(os.getcwd(), "data")
    ppd_model = model.PPD_Model(weights = [0.15, 0.35, 0.5], home_field=0.0)
    model_timeline = [2008, 2018]
    correct_outcome = []
    diff_error = []
    total_error = []
    home_score_error = []
    away_score_error = []
    print_outcome = False
    for game in games_df.itertuples(name='Game'):
        outstr = game.home_team + " v " + game.away_team + " " + str(game.season) + "\n"
        current_season = game.season
        model_timeline = [current_season - 3, current_season]
        predicted_game = game.id
        pred_game = matchup.Matchup(game.home_team, game.away_team, ppd_model, data_dir=data_dir)
        pred_winner, pred_diff, pred_total, pred_home_points, pred_away_points = pred_game.predict(model_timeline, predicted_game)
        correct_outcome += [pred_winner == game.winner]
        diff_error += [game.point_differential - pred_diff[0]]
        total_error += [game.total_points - pred_total[0]]
        home_score_error += [game.home_points - pred_home_points]
        away_score_error += [game.away_points - pred_away_points]
        outstr += "\npredicted outcome: " + str(correct_outcome[-1]) + "\n"
        outstr += "differential error: " + str(diff_error[-1]) + "\n"
        outstr += "total points error: " + str(total_error[-1]) + "\n"
        outstr += "home points error: " + str(home_score_error[-1]) + "\n"
        outstr += "away points error: " + str(away_score_error[-1]) + "\n" + "\n"
        if print_outcome:
            print(outstr)
    return correct_outcome, diff_error, total_error, home_score_error, away_score_error

if __name__ == '__main__':
    data_dir = os.path.join(os.getcwd(), "data")
    model_timeline = [2008, 2018]
    data_timeline = [2005, 2018]
    output_csv_file = "accuracy.csv"
    # weights = [0.15, 0.35, 0.5, 0.0]
    # weights = [0.15, 0.35, 0.5, 3.0]
    # weights = [0.1, 0.2, 0.7, 0.0]
    weights = [0.0, 0.4, 0.6, 0.0]


    game_data = fetch_data.get_game_data(timeline=model_timeline, data_dir=data_dir)
    model_data = model_analysis.process_game_data(game_data)
    ppd_model = model.PPD_Model(weights = weights[:3], home_field=weights[3])


    # ! Only uncomment to download all team drive data
    # for game in model_data.itertuples(name='Game'):
    #     home_team = team.Team(game.home_team, data_dir=data_dir)
    #     away_team = team.Team(game.away_team, data_dir=data_dir)
    #     home_team.get_drive_data(timeline=data_timeline)
    #     away_team.get_drive_data(timeline=data_timeline)

    # tamu = team.Team("Texas A&M", data_dir=data_dir)
    # tamu.get_drive_data(timeline=data_timeline)

    # sjs = team.Team("San José State", data_dir=data_dir)
    # sjs.get_drive_data(timeline=data_timeline)
    ngames = len(model_data.index)

    jobs_per_proc = int(ngames / cpu_count())
    leftover_jobs = ngames % cpu_count()
    jobs = []
    drift = 0
    for i in range(cpu_count()):
        start = i * jobs_per_proc
        if i < leftover_jobs:
            drift += 1
        end = (i * jobs_per_proc + jobs_per_proc + drift)
        game_set = model_data[start:end]
        jobs += [game_set]

    with Pool(cpu_count()) as pool:
        correct_o, diff_e, total_e, home_score_e, away_score_e = zip(*pool.map(validation_func, jobs))
    
    correct_outcome = [j for i in correct_o for j in i]
    diff_error = [j for i in diff_e for j in i]
    total_error = [j for i in total_e for j in i]
    home_score_error = [j for i in home_score_e for j in i]
    away_score_error = [j for i in away_score_e for j in i]

    perc_correct = (correct_outcome.count(True) / len(correct_outcome)) * 100
    np_diff_error = np.array(diff_error)
    np_total_error = np.array(total_error)
    np_home_score_error = np.array(home_score_error)
    np_away_score_error = np.array(away_score_error)

    mean_diff_error = np_diff_error.mean()
    std_diff_error = np.std(np_diff_error)
    mean_total_error = np_total_error.mean()
    std_total_error = np.std(np_total_error)
    mean_home_score_error = np_home_score_error.mean()
    std_home_score_error = np.std(np_home_score_error)
    mean_away_score_error = np_away_score_error.mean()
    std_away_score_error = np.std(np_away_score_error)

    csv_output_list = [perc_correct, mean_diff_error, std_diff_error, mean_total_error, std_total_error, mean_home_score_error, std_home_score_error, mean_away_score_error, std_away_score_error]

    # csv_output_str = "w1,w2,w3,hf,per_corr,de_mean,de_std,tp_mean,tp_std,hpe_mean,hpe_std,ape_mean,ape_std\n"
    # csv_output_str += ','.join([str(w) for w in weights]) + ','.join([str(o) for o in csv_output_list]) + "\n"
    csv_output_str = ','.join([str(w) for w in weights]) + "," + ','.join([str(o) for o in csv_output_list]) + "\n"
    with open(output_csv_file, "a+") as ocsv:
        ocsv.write(csv_output_str)

    print("%.2f percent correct" % perc_correct)
    print("differential error: %.4f mean and %.4f std dev" %(mean_diff_error, std_diff_error))
    print("total points error: %.4f mean and %.4f std dev" %(mean_total_error, std_total_error))
    print("home points error: %.4f mean and %.4f std dev" %(mean_home_score_error, std_home_score_error))
    print("away points error: %.4f mean and %.4f std dev" %(mean_away_score_error, std_away_score_error))

