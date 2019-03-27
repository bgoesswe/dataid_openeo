from git import Repo
from datetime import datetime
import pytz
import git
import json
import os
utc = pytz.UTC

def get_commit_by_timestamp(repo, timestamp):
    date_buffer = None
    git_info = {}
    for commit in repo.iter_commits("master"):
        commit_date = commit.committed_datetime
        if commit_date <= timestamp:
            if date_buffer:
                if commit_date > date_buffer:
                    date_buffer = commit_date
                    git_info["branch"] = commit.name_rev.split(" ")[1]
                    git_info["commit"] = commit.name_rev.split(" ")[0]

            else:
                date_buffer = commit_date
                git_info["branch"] = commit.name_rev.split(" ")[1]
                git_info["commit"] = commit.name_rev.split(" ")[0]

    return git_info

timestamp_text = "20180528101608.659892"


timestamp = datetime.strptime(timestamp_text, '%Y%m%d%H%M%S.%f')#datetime(2018, 5, 5, 23, 30,tzinfo=utc)
timestamp = pytz.utc.localize(timestamp)

repo = Repo("/data/MASTER/REPO/openeo-openshift-driver/")


#print(str(get_commit_by_timestamp(repo, timestamp))+str(timestamp))

filter_args_str = "{'bands': None, 'data_id': None, 'derived_from': None, 'extent': {'extent': {'crs': 'EPSG:4326', 'east': 17.171631, 'north': 49.041469, 'south': 46.517296, 'west': 9.497681}}, 'license': None, 'name': 's2a_prd_msil1c', 'time': {'extent': ['2017-01-01', '2017-01-31']}}"
filter_args_str = filter_args_str.replace("'", "\"")
filter_args_str = filter_args_str.replace("None", "null")
print(filter_args_str)
filter_args = json.loads(filter_args_str)
print(filter_args)

def display_text_file(file):
    with open(file.path) as fp:
        return fp.read()

display_text_file(None)