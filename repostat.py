import operator
import os
import requests
import svn.remote

def get_subdir_list(dir):
    with os.scandir(dir) as it:
        return [x.name for x in it if x.is_dir()]

# get list of local repos
def get_local_repos(path):
    return get_subdir_list(path)

# link to json file describing remote repos
json_url = "http://www.example.com/"

# get list of remote repos
def get_remote_repos(user, password):
    total_count = 0
    offset = 0
    limit = 0

    r = requests.get(json_url)
    if r.status_code == 200:
        d = r.json()
        total_count = d['total_count']
        offset = d['offset']
        limit = d['limit']
    else:
        return []

    repos = []
    while offset <= total_count:
        r = requests.get(json_url,
                         params={'offset': offset})
        if r.status_code == 200:
            d = r.json()
            repos += d['projects']
            offset += d['limit']
        else:
            print(r.status_code)

    return [r['identifier'] for r in repos]

def make_commit_table_entry(repo_name, log_entry):
    return {
        'repository': repo_name,
        'revision': log_entry.revision,
        'author': log_entry.author,
        'author_real': find_by_alias(log_entry.author),
        'date': log_entry.date.isoformat(),
        'year': log_entry.date.year,
        'month': log_entry.date.month,
        'day': log_entry.date.day,
        'hour': log_entry.date.hour,
        'minute': log_entry.date.minute,
        'second': log_entry.date.second,
        'microsecond': log_entry.date.microsecond,
        'message': log_entry.msg if log_entry.msg else ""
        }

# create commit table for svn repo
def get_commits_from_repo(repo_path):
    table = []
    r = svn.remote.RemoteClient(repo_path)
    try:
        repo_name = r.info()['entry_path']
        for log_entry in r.log_default():
            table.insert(0, make_commit_table_entry(repo_name, log_entry))
    except svn.exception.SvnException:
        print("SvnException")
        return []

    return table

# create aggregate commit table for all repos in list
def get_commits_from_repos(repo_path, repo_list):
    table = []

    print("Getting commits from {}".format(repo_path))
    for repo in repo_list:
        print("Checking repo {}...".format(repo))
        table += get_commits_from_repo(repo_path + repo)

    return table

# print commit statistics
def print_table(d, sort_by, reverse, header):
    total = 0
    for key in d:
        total += d[key]

    print("{}\tcommits\tpercentage".format(header))
    table_sorted = sorted(d.items(), key=operator.itemgetter(sort_by), reverse=reverse)
    for t in table_sorted:
        print("{}\t{}\t{:.2f}%"
              .format(t[0], t[1], t[1] / total * 100.0))
