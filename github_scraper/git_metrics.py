import sys
import csv
import re
import subprocess
import os
maxInt = sys.maxsize
decrement = True

# Code borrowed from:
# http://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072

while decrement:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

__author__ = 'Charles'


def main():
    with open('jruby.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open('results.csv', mode='w', newline='') as csv_file_out:
            fieldnames = csv_reader.fieldnames[0:27]
            commits = [commit for commit in csv_reader if re.search("^[a-z0-9]+$", commit['commit_hash'])]
            commit_hashes = [commit_hash['commit_hash'] for commit_hash in commits]
            print(commit_hashes)
            commit_lengths = [get_commit_length(commit_hash) for commit_hash in commit_hashes]
            print("Commit hashes: {} commit lengths {}", format(len(commit_hashes)), len(commit_lengths))
            fieldnames.append('commit_length')
            print(commit_lengths)
            commits = [update_dict(commit, commit_lengths, index)
                       for index, commit in enumerate(commits, start=0)]
            print(fieldnames)
            writer = csv.DictWriter(csv_file_out, fieldnames)
            writer.writeheader()
            commits = [filter_commits(commit, fieldnames) for commit in commits]
            writer.writerows(commits)


def filter_commits(commit, fieldnames):
    return {key: commit[key] for key in commit if fieldnames.__contains__(key)}


def update_dict(commit, commit_lengths, index):
    commit.update({'commit_length': commit_lengths[index]})
    return commit


def get_commit_length(commit_hash):
    os.chdir('jruby')
    git_commit_fields = ['id', 'author_name', 'date', 'message_header', 'message_body', 'extra']
    git_log_format = ['%H', '%an', '%ad', '%s', '%b']
    git_log_format = '%x1e' + '%x1f'.join(git_log_format) + '%x1f'
    options = ' show --format="%s" {}'.format(commit_hash)
    command = 'git' + options

    p = subprocess.Popen(command % git_log_format, shell=True, stdout=subprocess.PIPE)
    (log, _) = p.communicate()
    log = log.decode(encoding='ISO-8859-1')
    log = log.strip('\n\x1e').split("\x1e")
    log = (row.strip().split("\x1f") for row in log)
    log = (dict(zip(git_commit_fields, row)) for row in log)
    os.chdir('..')
    for commit in log:
        if not commit.__contains__('message_header'):
            return -1
        msg_bdy = commit.__contains__('message_body')
        if msg_bdy:
            return len(commit['message_header']) + len(commit['message_body'])
        else:
            return len(commit['message_header'])


if __name__ == '__main__':
    main()
