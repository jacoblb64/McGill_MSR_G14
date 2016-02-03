import sys
import csv
import re
import subprocess
import os
import argparse
import ntpath
import concurrent.futures
import multiprocessing

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
        maxInt = int(maxInt / 10)
        decrement = True


# Parallel 113.13 seconds
# Parallel + write
# Sequential time 172.2 seconds
# Sequential + write 97.257 seconds

fieldnames = ['commit_hash', 'commit_message', 'fix', 'classification', 'contains_bug', 'ns',
              'nd', 'nf', 'entrophy', 'la', 'ld', 'lt', 'ndev', 'age', 'nuc', 'exp', 'rexp', 'sexp',
              'glm_probability', 'project_name', 'commit_words', 'commit_structure']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='.', dest='project_path', type=str,
                        metavar='/home/Downloads/', help='project folder name')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('-f', '--filename', dest='csv_path', metavar='data.csv',
                        type=str, help='csv file including path')
    source.add_argument('-d', '--directory', type=str, metavar='/home/user/Downloads/',
                        help='The directory containing the csv files')
    parser.add_argument('-o', '--output', type=str, metavar='results.csv',
                        default='results.csv', help='The output filename')

    args = parser.parse_args()

    project_path = args.project_path
    csv_path = args.csv_path

    files = []

    if args.directory:
        # The directory option was picked
        project_name = 'merged'
        print('Looking at directory')
        for filename in os.listdir(args.directory):
            if filename.endswith('.csv'):
                files.append(os.path.join(args.directory, filename))

    else:
        print('Looking at single file')
        files.append(csv_path)
        project_name = os.path.splitext(ntpath.basename(csv_path))[0]

    if args.output != 'results.csv':
        out_file = args.output
    else:
        out_file = project_name + '_results.csv'

    if project_path is not '.':
        out_file = os.path.join(project_path, out_file)

    print('Writing output to ' + out_file)

    set_up(out_file, files)

    # with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    # for file in files:
    # Do some work here
    # executor.submit(parse_file, file, project_path, commit_struct_pat)
    # executor.shutdown(wait=True)
    # parse_file(csv_path, project_path, commit_struct_pat)


def parse_file(filename, commit_struct_pat, queue: multiprocessing.Queue):
    project_name = os.path.splitext(ntpath.basename(filename))[0]
    with open(filename) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        commits = []
        for commit in csv_reader:
            if re.search("^[a-z0-9]+$", commit['commit_hash']):
                commit_words = len(re.findall(r'\w+', commit['commit_message']))
                commit_structure = False
                if re.search(commit_struct_pat, commit['commit_message']):
                    commit_structure = True
                commit.update({'commit_words': commit_words})
                commit.update({'commit_structure': commit_structure})
                commit.update({'project_name': project_name})
                commit = {key: commit[key] for key in commit if key in fieldnames}
                commits.append(commit)
        else:
            queue.put(list(commits))


def file_writer(dest_filename, queue, token):
    with open(dest_filename, mode='w', newline='') as dest_file:

        writer = csv.DictWriter(dest_file, fieldnames)
        writer.writeheader()
        while True:
            data = queue.get()
            if data == token:
                return
            for commit in data:
                writer.writerow(commit)


def set_up(outfile: str, files: list):
    commit_struct_pat = re.compile('^(.{,20})((\[)|(fix)|(close)|(#\d+)|(sign)|(release)|(upgrade)|(bug)|(version)|'
                                   '(id))', re.IGNORECASE | re.MULTILINE)
    queue = multiprocessing.Queue()

    stop_token = ''
    writer_process = multiprocessing.Process(target=file_writer, args=(outfile, queue, stop_token))
    writer_process.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for file in files:
            # Do some work here
            executor.submit(parse_file, file, commit_struct_pat, queue)
        executor.shutdown(wait=True)

    # Dispatch jobs

    # Make sure finished

    queue.put(stop_token)
    writer_process.join()


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
