import requests
def get_cfb_odds(self):
    try:
        source = requests.get("https://www.bovada.lv/services/sports/event/v2/events/A/description/football/college-football").json()
    except:
        raise ConnectionError("url is likely not responding")
    
    # TODO loop through source and get all the available matchups (total, spread, and moneylin)

if __name__ == "__main__":
    pass
    # matchups, odds = get_cfb_odds()
    # TODO execute ppd model on each matchup
    # TODO calculate any helpful probabilities (prob_spread, prob_total, and percentiles of those probabilities (model is rarely this wrong sort of thing))
    # TODO all the relevant stuff to a csv
    # TODO: analysis_date.csv: away team @ home team, home team spread, home team spread odds, away team spread odds, home team moneyline odds,
    # TODO                      away team moneyline odds, total points, over odds, under odds, pred_spread, prob_spread, prob_prob_spread, 
    # TODO:                     prob_winner, prob_prob_winner, pred_total, prob_total, prob_prob_total, home spread bet, away spread bet,
    # TODO:                     home moneyline bet, away moneyline bet, over bet, under bet
    # TODO: instead of probabilities calcualted from normals, just count the aboves and belows from the validation_data