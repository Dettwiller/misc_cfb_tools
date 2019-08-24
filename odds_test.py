from football_modeling import tools, fetch_data

cbf_downloader = fetch_data.data_downloader()
fbs_teams_df = cbf_downloader.get_all_fbs_teams()
fbs_teams_list = fbs_teams_df['school'].tolist()

tools.get_cfb_odds(fbs_teams_list)