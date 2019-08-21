from collections import namedtuple
from csv import reader
from datetime import datetime
from os import getcwd
from os.path import join
from warnings import warn

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import norm

from football_modeling import fetch_data, model, team, tools


def evaluator(model_timeline, data_timeline, data_dir=getcwd(), games_dir=getcwd(), modeling_data_dir=getcwd()):
    evaluator_obj = Evaluator(model_timeline, data_timeline, data_dir=data_dir, games_dir=games_dir, modeling_data_dir=modeling_data_dir)
    return evaluator_obj

class Evaluator:
    def __init__(self, model_timeline, data_timeline, data_dir=getcwd(), games_dir=getcwd(), modeling_data_dir=getcwd()):
        tools.timeline_check(model_timeline)
        tools.timeline_check(data_timeline)
        tools.directory_check(data_dir)
        tools.directory_check(games_dir)
        tools.directory_check(modeling_data_dir)
        data_dir_check = data_dir in [games_dir, modeling_data_dir]
        games_dir_check = games_dir in [data_dir, modeling_data_dir]
        modeling_data_dir_check = modeling_data_dir in [data_dir, games_dir]
        if data_dir_check or games_dir_check or modeling_data_dir_check:
            warn("data_dir, games_dir, and modeing_data_dir are not unique.")

        self.model_timeline = model_timeline
        self.data_timeline = data_timeline
        self.data_dir = data_dir
        self.games_dir = games_dir
        self.modeling_data_dir = modeling_data_dir
        self.data_downloader = fetch_data.data_downloader(data_dir=data_dir)
        self.eval_file = join(self.data_dir, "eval.csv")
        self.results_file = join(self.data_dir, "results.csv")

        self.model_data_type = ""

        self.running_wins = 0.0
        self.running_spread_prob = 0.0
        self.running_total_prob = 0.0
        self.running_pred_num = 0

    def __update_timeline(self, timeline_type, new_timeline):
        if timeline_type is 'model' and new_timeline is not None:
            tools.timeline_check(new_timeline)
            if new_timeline != self.model_timeline:
                warn("supplied model_timeline is different from current model_timeline, updating model_timeline")
                self.model_timeline = new_timeline
        elif timeline_type is 'data' and new_timeline is not None:
            tools.timeline_check(new_timeline)
            if new_timeline != self.data_timeline:
                warn("supplied data_timeline is different from current data_timeline, updating data_timeline")
                self.data_timeline = new_timeline

    def __check_data_type(self, data_type):
        data_types_type_check = isinstance(data_type, str)
        assert data_types_type_check, "data_type is not string: %r" % type(data_type)
        data_types_value_check = data_type in self.data_downloader.acceptable_data_types
        assert data_types_value_check, "data_type (" + data_type + ") must be one of: %r" % self.data_downloader.acceptable_data_types
        if not self.model_data_type:
            self.model_data_type = data_type
        else:
            model_data_check = self.model_data_type == data_type
            assert model_data_check, "provided data_type does not match current model_data_type"

    def __get_full_game_list(self, team_names):
        desired_data = ["id", "away_team", "away_points", "home_team", "home_points", "neutral_site", "season"]
        Game = namedtuple('Game', 'id away_team away_points home_team home_points neutral_site season')
        full_game_list = []
        for team_name in team_names:
            csv_filename = team_name + "_games_data_" + str(self.model_timeline[0]) + "-" + str(self.model_timeline[1]) + ".csv"
            csv_file = join(self.games_dir, csv_filename)
            with open(csv_file, "r", encoding='utf-8', errors='ignore') as csvf:
                game_reader = reader(csvf, delimiter=',', quotechar='"')
                header_list = next(game_reader)
                desired_indices = [header_list.index(val) for val in desired_data]
                away_conference_i = header_list.index('away_conference')
                home_conference_i = header_list.index('home_conference')
                for game in game_reader:
                    if game[away_conference_i] is not None and game[home_conference_i] is not None:
                        temp_game_list = [game[val] for val in desired_indices]
                        temp_game_tuple = Game(*temp_game_list)
                        if temp_game_tuple.away_team in team_names and temp_game_tuple.home_team in team_names:
                            full_game_list += [temp_game_tuple]
                        # else:
                        #     print("banned " + temp_game_tuple.season + " " + temp_game_tuple.away_team + " @ " + temp_game_tuple.home_team)
                    #     else:
                    #         print("banned " + temp_game_tuple.season + " " + temp_game_tuple.away_team + " @ " + temp_game_tuple.home_team)
                    # else:
                    #     print("ignoring " + temp_game_tuple.season + " " + temp_game_tuple.away_team + " @ " + temp_game_tuple.home_team)

        return full_game_list

    def __predict_game(self, game_tuple, home_team, away_team, eval_model, print_progress):
        # ('Game', 'id away_team away_points home_team home_points neutral_site season')
        if print_progress:
            print("predicting: " + game_tuple.away_team + " @ " + game_tuple.home_team)
        true_total = float(game_tuple.home_points) + float(game_tuple.away_points)
        true_spread = float(game_tuple.home_points) - float(game_tuple.away_points)

        if game_tuple.neutral_site == "False":
            neutral_site = False
        else:
            print(game_tuple.neutral_site)
            neutral_site = True

        total_dist, spread_dist = eval_model.predict(home_team, away_team, timeline=self.data_timeline,
            predicted_game_id=int(game_tuple.id), neutral_site=neutral_site, print_progress=print_progress)

        pred_spread = spread_dist[0]
        pred_total = total_dist[0]
        pred_home_points = (total_dist[0] + spread_dist[0]) / 2
        pred_away_points = (total_dist[0] - spread_dist[0]) / 2

        total_error = pred_total - true_total
        spread_error = pred_spread - true_spread
        home_error = pred_home_points - float(game_tuple.home_points)
        away_error = pred_away_points -float(game_tuple.away_points)

        prob_away_win = norm.cdf(0.0, spread_dist[0], np.sqrt(spread_dist[1]))
        prob_home_win = 1.0 - prob_away_win

        if float(game_tuple.home_points) > float(game_tuple.away_points):
            prob_winner = prob_home_win
        elif float(game_tuple.home_points) < float(game_tuple.away_points):
            prob_winner = prob_away_win
        else:
            prob_winner = 0.0 # lol ties

        if true_total <= total_dist[0]:
            prob_total = norm.cdf(true_total, total_dist[0], np.sqrt(total_dist[1])) * 2.0
        else:
            prob_total = (1.0 - norm.cdf(true_total, total_dist[0], np.sqrt(total_dist[1]))) * 2.0

        if true_spread <= spread_dist[0]:
            prob_spread = norm.cdf(true_spread, spread_dist[0], np.sqrt(spread_dist[1])) * 2.0
        else:
            prob_spread = (1.0 - norm.cdf(true_spread, spread_dist[0], np.sqrt(spread_dist[1]))) * 2.0

        self.running_spread_prob = (self.running_spread_prob * self.running_pred_num + prob_spread) / (self.running_pred_num + 1.0)
        self.running_total_prob = (self.running_total_prob * self.running_pred_num + prob_total) / (self.running_pred_num + 1.0)
        self.running_pred_num += 1.0
        if prob_winner > 0.5:
            self.running_wins += 1
        running_win_perc = float(self.running_wins / float(self.running_pred_num))

        eval_list = [
            game_tuple.season, game_tuple.id, game_tuple.home_team, game_tuple.away_team,
            game_tuple.neutral_site, game_tuple.home_points, game_tuple.away_points, pred_home_points,
            pred_away_points, prob_winner, prob_spread, prob_total, total_error, spread_error, home_error, away_error
            ]
        eval_list_str = []
        for val in eval_list:
            if isinstance(val, float):
                eval_list_str += [str("{0:.4f}".format(val))]
            else:
                eval_list_str += [str(val)]
        # eval_file_header = "season,game_id,home_team,away_team,neutral_site,home_score,away_score,pred_home_score,pred_away_score"
        # eval_file_header += "prob_winner,prob_spread,prob_total,total_error,spread_error,home_error,away_error\n"
        eval_str = ','.join(eval_list_str) + "\n"
        output_str = "mean spread prob = " + str(self.running_spread_prob) + "\n"
        output_str += "mean total prob = " + str(self.running_total_prob) + "\n"
        output_str += "running win per = " + str(running_win_perc) + "\n"
        with open(self.results_file, "a", encoding='utf-8') as rf:
            rf.write(eval_str)
        if print_progress:
            print(eval_str)
            print(output_str)

    # def download_game_data(self, model_timeline=None, print_progress=False):
    #     self.__update_timeline('model', model_timeline)
    #     print_progress_type_check = isinstance(print_progress, bool)
    #     assert print_progress_type_check, "print_progress is not bool: %r" % type(print_progress)

    #     self.data_downloader.change_download_directory(self.games_dir)
    #     self.data_downloader.parallel_download_all_team_data(data_type='games', timeline=model_timeline, print_progress=print_progress)

    # def download_model_data(self, data_timeline=None, data_type='drives', print_progress=False):
    #     self.__update_timeline('data', data_timeline)
    #     self.__check_data_type(data_type)
    #     print_progress_type_check = isinstance(print_progress, bool)
    #     assert print_progress_type_check, "print_progress is not bool: %r" % type(print_progress)

    #     self.data_downloader.change_download_directory(self.modeling_data_dir)
    #     self.data_downloader.parallel_download_all_team_data(data_type=self.model_data_type, timeline=data_timeline, print_progress=True)

    def __visualize_results(self, np_spread_errors, np_total_errors, np_prob_spread, np_prob_total, np_win_win_probs, np_loss_win_probs):
        plt.hist(np_spread_errors)
        plt.title("Spread Errors")
        plt.savefig(join(self.data_dir, "spread_errors"))
        plt.clf()

        plt.hist(np_total_errors)
        plt.title("Total Errors")
        plt.savefig(join(self.data_dir, "total_errors"))
        plt.clf()

        plt.hist(np_prob_spread)
        plt.title("Spread Probabilities")
        plt.savefig(join(self.data_dir, "prob_spread"))
        plt.clf()

        plt.hist(np_prob_total)
        plt.title("Total Probabilities")
        plt.savefig(join(self.data_dir, "prob_total"))
        plt.clf()

        plt.hist(np_win_win_probs)
        plt.title("Win Probabilities of Wins")
        plt.savefig(join(self.data_dir, "win_win_prob"))
        plt.clf()

        plt.hist(np_loss_win_probs)
        plt.title("Win Probabilities of Losses")
        plt.savefig(join(self.data_dir, "loss_win_prob"))
        plt.clf()

        plt.hist(np_win_win_probs)
        plt.hist(np_loss_win_probs)
        plt.title("Win Probabilities of Wins and Losses")
        plt.savefig(join(self.data_dir, "win_probs_overlay"))
        plt.clf()

    def __evaluate_csv(self):
        spread_errors = []
        total_errors = []
        correct_pred_wins = 0.0
        games = 0.0
        win_win_probs = []
        loss_win_probs = []
        prob_spread = []
        prob_total = []
        with open(self.results_file, "r", encoding='utf-8') as rf:
            line = rf.readline() # header
            # season, game_id, home_team, away_team, neutral_site, home_score, away_score, pred_home_score, pred_away_score,
            # prob_winner, prob_spread, prob_total, total_error, spread_error, home_error, away_error
            line = rf.readline() # content
            while line:
                list_line = line.strip().split(',')

                spread_errors += [float(list_line[13])]
                total_errors += [float(list_line[12])]
                prob_spread += [float(list_line[10])]
                prob_total += [float(list_line[11])]
                if float(list_line[9]) > 0.5:
                    win_win_probs += [float(list_line[9])]
                    correct_pred_wins += 1.0
                else:
                    loss_win_probs += [1.0 - float(list_line[9])]
                line = rf.readline() # content
                games += 1.0
        np_spread_errors = np.array(spread_errors)
        np_total_errors = np.array(total_errors)
        np_prob_spread = np.array(prob_spread)
        np_prob_total = np.array(prob_total)
        np_win_win_probs = np.array(win_win_probs)
        np_loss_win_probs = np.array(loss_win_probs)

        rmse_spread = np.sqrt(np.mean(np_spread_errors ** 2.0))
        rmse_total = np.sqrt(np.mean(np_total_errors ** 2.0))
        win_perc = float(correct_pred_wins / games )
        spread_prob_mean = np.mean(np_prob_spread)
        spread_prob_sigma = np.std(np_prob_spread)
        total_prob_mean = np.mean(np_prob_total)
        total_prob_sigma = np.std(np_prob_total)
        win_win_prob_mean = np.mean(np_win_win_probs)
        win_win_prob_sigma = np.std(np_win_win_probs)
        loss_win_prob_mean = np.mean(np_loss_win_probs)
        loss_win_prob_sigma = np.std(np_loss_win_probs)
        self.__visualize_results(np_spread_errors, np_total_errors, np_prob_spread, np_prob_total, np_win_win_probs, np_loss_win_probs)

        results = [
            rmse_spread, rmse_total, spread_prob_mean, spread_prob_sigma,
            total_prob_mean, total_prob_sigma, win_perc, win_win_prob_mean,
            win_win_prob_sigma, loss_win_prob_mean, loss_win_prob_sigma
            ]

        str_results = [str("{0:.4f}".format(val)) for val in results]

        results_header = "RMSE spread,RMSE total,spread prob mean,spread prob sigma,total prob mean,total prob sigma,"
        results_header += "win perc,correct winner win prob mean,correct winner win prob sigma,"
        results_header += "incorrect winner win prob mean,incorrect winner win prob sigma\n"

        results_line = ','.join(str_results)
        with open(self.eval_file, "w+", encoding='utf-8') as ef:
            ef.write(results_header)
            ef.write(results_line)

    def evaluate_model(self, eval_model, model_timeline=None, data_timeline=None, data_type='drives', print_progress=False):
        self.__update_timeline('model', model_timeline)
        self.__update_timeline('data', data_timeline)
        model_type_check = isinstance(eval_model, model.Model)
        assert model_type_check, "model is not valid instance of model.Model"
        self.__check_data_type(data_type)
        print_progress_type_check = isinstance(print_progress, bool)
        assert print_progress_type_check, "print_progress is not bool: %r" % type(print_progress)

        fbs_teams_df = self.data_downloader.get_all_fbs_teams()
        fbs_teams_list = fbs_teams_df['school'].tolist()

        if self.model_data_type == 'drives':
            drives_dir = self.modeling_data_dir
        else:
            drives_dir = getcwd()

        teams_dict = {}
        for fbs_team in fbs_teams_list:
            teams_dict[fbs_team] = team.team(fbs_team, data_dir=self.data_dir, games_dir=self.games_dir, drives_dir=drives_dir)
            # *teams_dict[fbs_team].get_data(data_timeline, data_type='drives', print_progress=print_progress)
            # *teams_dict[fbs_team].get_data(model_timeline, data_type='games', print_progress=print_progress)
            teams_dict[fbs_team].get_data(data_timeline, data_type='drives', print_progress=False)
            teams_dict[fbs_team].get_data(model_timeline, data_type='games', print_progress=False)

        ("id", "away_team", "away_points", "home_team", "home_points", "neutral_site", "season")
        full_game_list = self.__get_full_game_list(fbs_teams_list)

        results_file_header = "season,game_id,home_team,away_team,neutral_site,home_score,away_score,pred_home_score,pred_away_score,"
        results_file_header += "prob_winner,prob_spread,prob_total,total_error,spread_error,home_error,away_error\n"
        with open(self.results_file, "w+", encoding='utf-8') as rf:
            rf.write(results_file_header)


        for game in full_game_list:
            if tools.new_fbs_schools_check(game):
                self.__predict_game(game, teams_dict[game.home_team], teams_dict[game.away_team], eval_model, print_progress)

        # self.__evaluate_csv()
