import sys
import csv
import re
import os
import argparse
import ntpath
import concurrent.futures
import multiprocessing
from nltk.corpus import stopwords
from nltk import sent_tokenize

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
              'glm_probability', 'project_name', 'commit_words']


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


def parse_file(filename: str, queue: multiprocessing.Queue, stop_words: set):
    project_name = os.path.splitext(ntpath.basename(filename))[0]
    with open(filename) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        commits = []
        for commit in csv_reader:
            if re.search("^[a-z0-9]+$", commit['commit_hash']):
                useful_words = [word for sentence in sent_tokenize(commit['commit_message'])
                                for word in re.findall(r'\w+', sentence, flags=re.UNICODE | re.LOCALE)
                                if word not in stop_words]
                # commit_words = len(re.findall(r'\w+', commit['commit_message']))
                commit_words = len(useful_words)
                commit.update({'commit_words': commit_words})
                commit.update({'project_name': project_name})
                commit = {key: commit[key] for key in commit if key in fieldnames}
                commits.append(commit)
        else:
            queue.put(list(commits))


def file_writer(dest_filename, queue: multiprocessing.Queue, token):
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

    queue = multiprocessing.Queue()

    stop_words = stopwords.words('english')
    with open('stop-word-list.txt', mode='r') as stop_word_file:
        for line in stop_word_file:
            cur_line = line.replace('\n', '')
            if cur_line not in stop_words:
                stop_words.append(cur_line)
        else:
            stop_words = set(stop_words)
    stop_token = ''
    writer_process = multiprocessing.Process(target=file_writer, args=(outfile, queue, stop_token))
    writer_process.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for file in files:
            # Dispatch jobs
            executor.submit(parse_file, file, queue, stop_words)
        executor.shutdown(wait=True)

    queue.put(stop_token)
    writer_process.join()


if __name__ == '__main__':
    main()
