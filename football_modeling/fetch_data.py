from collections.abc import Iterable
from datetime import datetime
from os import getcwd
from os.path import isfile, join

import pandas as pd
import requests

from football_modeling import tools


def data_downloader(website_api="https://api.collegefootballdata.com", data_dir=getcwd()):
    downloader = DataDownloader(website_api=website_api, data_dir=data_dir)
    return downloader

class DataDownloader():
    def __init__(self, website_api="https://api.collegefootballdata.com", data_dir=getcwd()):
        _ = tools.website_check(website_api)
        tools.directory_check(data_dir)

        self.website_api = website_api
        self.data_dir = data_dir
        self.problem_teams = {"Texas A&M": "Texas%20A%26M", "San José State": "San%20Jos%C3%A9%20State"}

    def __print_download_progress(self, years, i_year, entities, i_entity):
        n_entities = len(entities)
        if i_entity >= n_entities:
            i_entity = 0
            i_year += 1
        status = str(years[i_year]) + " " + entities[i_entity]
        print(status)
        i_entity += 1
        return i_year, i_entity

    def __define_queries(self, data_type, entity_type, entities, timeline):
        base_query = self.website_api + "/" + data_type + "?"
        queries = []
        for year_int in range(timeline[0], timeline[1]+1):
            year_query = base_query
            year_str = str(year_int)
            year_query += "year=" + year_str
            for entity in entities:
                entity_query = year_query
                entity_query += "&" + entity_type + "=" + entity
                queries += [entity_query]
        return queries

    def __download_query(self, query, data_type, year, target_df):
        query_json = requests.get(query).json()
        query_df = pd.DataFrame(query_json)
        if data_type == 'drives':
            query_df['season'] = str(year)
        if target_df:
            if not query_df.empty:
                target_df = target_df.append(query_df, ignore_index=True)
            final_df = target_df
        else:
            final_df = query_df
        return final_df

    def __download_queries(self, queries, data_type, entity_type, entities, timeline, print_progress):
        years = range(timeline[0], timeline[1])
        i_year = 0
        i_entity = 0
        if print_progress:
            i_year, i_entity = self.__print_download_progress(years, i_year, entities, i_entity)
        data_df = self.__download_query(queries[0], data_type, years[0], False)
        for query in queries[1:]:
            data_df = self.__download_query(query, data_type, years[i_year], data_df)
            if print_progress:
                i_year, i_entity = self.__print_download_progress(years, i_year, entities, i_entity)
        return data_df

    def __download_data(self, csv_filename, data_type, entity_type, entities, timeline, print_progress):
        queries = self.__define_queries(data_type, entity_type, entities, timeline)
        assert queries, "queries is empty %r" % str(queries)

        data_df = self.__download_queries(queries, data_type, entity_type, entities, timeline, print_progress)
        data_df.to_csv(join(self.data_dir, csv_filename))
        return data_df

    def __get_data_input_checking(self, teams, conferences, data_type, timeline, print_progress):
        teams_type_check = isinstance(teams, Iterable)
        assert teams_type_check, "teams is not iterable: %r" % type(teams)
        team_type_check = all([isinstance(team, str) for team in teams])
        assert team_type_check, "team names in teams are not all strings: %r" % teams
        conferences_type_check = isinstance(conferences, Iterable)
        assert conferences_type_check, "conferences is not iterable: %r" % type(conferences)
        conference_type_check = all([isinstance(conference, str) for conference in conferences])
        assert conference_type_check, "conference names in conferences are not all strings: %r" % conferences
        data_types_type_check = isinstance(data_type, str)
        assert data_types_type_check, "data_type is not string: %r" % type(data_type)
        acceptable_data_types = ['games', 'drives']
        data_types_value_check = data_type in acceptable_data_types
        assert data_types_value_check, "data_type (" + data_type + ") must be one of: %r" % acceptable_data_types
        tools.timeline_check(timeline)
        print_progress_type_check = isinstance(print_progress, bool)
        assert print_progress_type_check, "print_progress is not bool: %r" % type(print_progress)
        validity_check = conferences or teams
        assert validity_check, "teams and conferences are both False (empty)"
        if conferences and teams:
            raise Warning("teams query(ies) will be masked by conference query(ies)")

    def get_data(self, teams=[], conferences=[], data_type='games', timeline=[1800, datetime.now().year-1], print_progress=False):
        self.__get_data_input_checking(teams, conferences, data_type, timeline, print_progress)

        if conferences:
            entities = conferences
            entity_type = "conference"
        else:
            entities = teams
            entity_type = "team"

        requested_data_frames = {}
        for entity in entities:
            csv_filename = entity + "_" + data_type + "_data_" + str(timeline[0]) + "-" + str(timeline[1]) + ".csv"
            tools.csv_subdata_search(csv_filename, self.data_dir)
            csv_file = join(self.data_dir, csv_filename)
            if isfile(csv_file):
                with open(csv_file, 'r', encoding='utf-8') as csvf:
                    entity_df = pd.read_csv(csvf)
            else:
                entity_df = self.__download_data(csv_filename, data_type, entity_type, entities, timeline, print_progress)
            requested_data_frames[entity] = entity_df.copy(deep=True)
        return requested_data_frames
