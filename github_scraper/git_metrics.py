import sys
import csv
import re
import subprocess
import os
import argparse
import ntpath

__author__ = 'Charles'

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

# Parallel 113.13 seconds
# Parallel + write
# Sequential time 172.2 seconds
# Sequential + write 97.257 seconds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='.', dest='project_path', type=str,
                        metavar='/home/Downloads/', help='project folder name')
    parser.add_argument('-f', '--filename', dest='csv_path', required=True, metavar='data.csv',
                        type=str, help='csv file including path')

    args = parser.parse_args()
    project_path = args.project_path
    csv_path = args.csv_path

    commit_struct_pat = re.compile('^(.{,20})((\[)|(fix)|(close)|(#\d+)|(sign)|(release)|(upgrade)|(bug)|(version))', re.IGNORECASE | re.MULTILINE)
    with open(csv_path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        print(os.path.splitext(ntpath.basename(csv_path))[0])
        if project_path is not '.':
            out_file = os.path.join(project_path, (os.path.splitext(ntpath.basename(csv_path))[0] + '_results.csv'))
        else:
            out_file = os.path.splitext(csv_path)[0] + '_results.csv'
        print(out_file)
        with open(out_file, mode='w', newline='') as csv_file_out:
            fieldnames = list()
            fieldnames.append(csv_reader.fieldnames[0])
            fieldnames += csv_reader.fieldnames[5:8] + csv_reader.fieldnames[9:27]
            fieldnames.append('commit_words')
            fieldnames.append('commit_structure')
            writer = csv.DictWriter(csv_file_out, fieldnames)
            writer.writeheader()
            for index, commit in enumerate(csv_reader):
                if re.search("^[a-z0-9]+$", commit['commit_hash']):
                    commit_words = len(re.findall(r'\w+', commit['commit_message']))
                    commit_structure = False
                    if re.search(commit_struct_pat, commit['commit_message']):
                        commit_structure = True
                    commit.update({'commit_words': commit_words})
                    commit.update({'commit_structure': commit_structure})
                    commit = {key: commit[key] for key in commit if key in fieldnames}
                    writer.writerow(commit)


def get_commit_length(commit_hash, project_path):
    os.chdir(project_path)
    git_commit_fields = ['id', 'author_name', 'date', 'message_header', 'message_body', 'extra']
    git_log_format = ['%H', '%an', '%ad', '%s', '%b']
    git_log_format = '%x1e' + '%x1f'.join(git_log_format) + '%x1f'
    options = ' log -n 1 --format="%s" {}'.format(commit_hash)
    command = 'git' + options

    p = subprocess.Popen(command % git_log_format, shell=True, stdout=subprocess.PIPE)
    (log, _) = p.communicate()
    log = log.decode(encoding='ISO-8859-1')
    log = log.strip('\n\x1e').split("\x1e")
    log = (row.strip().split("\x1f") for row in log)
    log = (dict(zip(git_commit_fields, row)) for row in log)
    os.chdir('..')
    for commit in log:
        if 'message_header' not in commit:
            print('Error: no commit header found')
            return 0
        msg_bdy = 'message_body' in commit

        if msg_bdy:
            return 1 + len(re.findall(r'\n', commit['message_body'])) + 1
        else:
            return 1


if __name__ == '__main__':
    main()
