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
    # TODO calculate any helpful probabilities
    # TODO all the relevant stuff to a csv