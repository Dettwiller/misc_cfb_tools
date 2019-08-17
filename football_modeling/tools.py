from os.path import isfile, exists, join, splitext
from os import listdir
import requests
from collections.abc import Iterable
from csv import reader, writer

def directory_check(directory):
    directory_file_check = isfile(directory)
    directory_exist_check = exists(directory)
    directory_error_statement = "directory does not exist: %r" % directory
    assert directory_exist_check and not directory_file_check, directory_error_statement

def file_check(filename, directory=False):
    filename_type_check = isinstance(filename, str)
    assert filename_type_check, "filename is not string: %r" % type(filename)
    if directory:
        directory_check(directory)
        file_path = join(directory, filename)
        file_exist_check = exists(file_path)
        assert file_exist_check, "directory indicates to check for file and file does not exist: %r" % file_path

def website_check(url):
    url_type_check = isinstance(url, str)
    assert url_type_check, "url is not a string: %r" % type(url)
    website_content = requests.get(url)
    website_request_check = website_content.status_code == 200
    assert website_request_check, "broken link or website is down"
    return website_content

def timeline_check(timeline):
    timeline_type_check = isinstance(timeline, Iterable)
    assert timeline_type_check, "timeline is not iterable: %r" % timeline
    timeline_len_check = len(timeline) == 2
    assert timeline_len_check, "timeline does not contain two elements: %r" % timeline
    timeline_value_check = timeline[1] >= timeline[0]
    assert timeline_value_check, "timeline is not ordered [lower, upper]: %r" % timeline

def csv_decomposer(csv_filename):
    file_check(csv_filename)

    csv_filename_split_list = csv_filename.split("_")
    start_year = int(csv_filename_split_list[-1].split("-")[0])
    end_year = int(csv_filename_split_list[-1].split("-")[-1].split(".")[0])
    timeline = [start_year, end_year]
    base_name = '_'.join(csv_filename_split_list[:-1])
    return base_name, timeline

def create_sub_csv(new_csv_filename, timeline, source_csv_filename, data_dir):
    file_check(new_csv_filename)
    timeline_check(timeline)
    directory_check(data_dir)
    file_check(source_csv_filename, data_dir)

    new_csv = join(data_dir, new_csv_filename)
    source_csv = join(data_dir, source_csv_filename)
    with open(source_csv, "r", encoding='utf-8', errors='ignore') as scsv:
        with open(new_csv, "w+", newline='', encoding='utf-8') as ncsv:
            source_reader = reader(scsv, delimiter=',')
            writer_obj = writer(ncsv, delimiter=',')
            header = next(source_reader, None)
            writer_obj.writerow(header)
            season_index = header.index('season') # * all .csv datafiles should be tagged by season
            line = next(source_reader, False)
            while line:
                season = int(line[season_index])
                if season >= timeline[0] and season <= timeline[1]:
                    writer_obj.writerow(line)
                line = next(source_reader, False)

def csv_subdata_search(csv_filename, data_dir):
    file_check(csv_filename)
    directory_check(data_dir)

    base_name, desired_timeline = csv_decomposer(csv_filename)
    data_dir_contents = iter(listdir(data_dir))
    searching = True
    while searching:
        item = next(data_dir_contents, False)
        if not item:
            searching = False
        elif item == csv_filename:
            searching = False
        else:
            pathed_item = join(data_dir, item)
            _, extension = splitext(pathed_item)
            if isfile(pathed_item) and extension == '.csv':
                candidate_base_name, candidate_timeline = csv_decomposer(item)
                name_match = candidate_base_name == base_name
                left_year = candidate_timeline[0] <= desired_timeline[0]
                right_year = candidate_timeline[1] >= desired_timeline[1]
                if name_match and left_year and right_year:
                    create_sub_csv(csv_filename, desired_timeline, pathed_item, data_dir)
                    searching = False