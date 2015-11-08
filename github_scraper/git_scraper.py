import subprocess
import os
import ntpath
import re
from statistics import mean
import concurrent.futures
import json

__author__ = 'Charles'


def main():
    # We need to get repo urls then we call call cd(repo_url)
    repo_urls = get_repo_urls(filename='boa-job-test.txt')  # Using this as dummy input file

    # Now we need to get the output for several repositories. We shall do this in parallel
    outputs = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
        for repo in repo_urls:
            future = executor.submit(get_repo_data, repo)
            outputs.append(future.result())
        executor.shutdown(wait=True)
    # repo_url = "https://bitbucket.org/cgathuru/dnsclient.git"  # Using this as a dummy repo_url
    # output = get_repo_data(repo_url)
    print("We got info for {} out of {} repositories".format(len(outputs), len(repo_urls)))
    # outputs = (' '.join(output) for output in outputs)
    with open("results.txt", 'a') as file:
        json.dump(outputs, file)
        file.close()


def get_repo_urls(filename):
    repo_urls = []
    rp = re.compile("(?P<repo_url>https://.+\.git)", re.IGNORECASE)

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            m = rp.search(line)
            if m:
                repo_urls.append(m.group('repo_url'))
                print(m.group('repo_url'))
        file.close()
    return repo_urls


def get_repo_data(repo_url):
    """
    This function mines the data from a repo
    :param repo_url: The url of the repo to mind
    :return: A list of data corresponding to each file that had a bug fix
    """
    repo_name = cd(repo_url)
    git_commit_fields = ['id', 'author_name', 'date', 'message_header', 'message_body', 'extra']
    git_log_format = ['%H', '%an', '%ad', '%s', '%b']
    git_log_format = '%x1e' + '%x1f'.join(git_log_format) + '%x1f'
    options = ' log --reverse --stat --format="%s"'
    command = 'git' + options

    p = subprocess.Popen(command % git_log_format, shell=True, stdout=subprocess.PIPE)
    (log, _) = p.communicate()
    log = log.decode(encoding='ISO-8859-1')
    log = log.strip('\n\x1e').split("\x1e")
    log = (row.strip().split("\x1f") for row in log)
    log = (dict(zip(git_commit_fields, row)) for row in log)

    # Now we need to count the number of line additions and deletions are
    # associated with a particular bug. To do this we will check the commit message
    bug_msg = re.compile("(?P<bug_word>bug|bugs|fix|fixed|fixes|fix\s+for|fixes\s+for|defects|patch)",
                         re.IGNORECASE | re.MULTILINE)

    count_bugs = 0
    commit_length = []
    num_commits = 0

    print("Analysing " + repo_name)

    # We need the average commit length, the number of bugs and number of commits
    for commit in log:

        if not commit.__contains__('message_body'):
            continue

        m1 = bug_msg.search(commit['message_header'])

        msg_bdy = commit.__contains__('message_body')
        if msg_bdy:
            m2 = bug_msg.search(commit['message_body'])
        else:
            m2 = False
        if m1 or m2:
            # If we are here then we have a match for a bug. We need to extract the
            # number of additions and deletions
            count_bugs += 1
        else:
            if msg_bdy:
                commit_length.append(len(commit['message_header']) + len(commit['message_body']))
            else:
                commit_length.append(len(commit['message_header']))
        num_commits += 1

    # Now we need to to get the average number of commits
    avg_commits = int(mean(commit_length))
    repo_content = {'repo_name': repo_name, 'avg_commits': str(avg_commits),
                    'num_bugs': str(count_bugs), 'num_commits': str(num_commits)}
    print(repo_content)
    return repo_content


def get_file_output(filename):
    """
    :param filename: The filename to search for bugs
    :return: A triple in format $filename $added_lns $removed_lns representing the number of added lines
    and removed lines that have bug fixes in them
    """
    git_commit_fields = ['id', 'author_name', 'date', 'message_header', 'message_body', 'extra']
    git_log_format = ['%H', '%an', '%ad', '%s', '%b']
    git_log_format = '%x1e' + '%x1f'.join(git_log_format) + '%x1f'
    options = ' log --follow -p --reverse --stat --format="%s"'
    command = 'git' + options

    p = subprocess.Popen(command % git_log_format + " " + filename, shell=True, stdout=subprocess.PIPE)
    (log, _) = p.communicate()
    log = log.decode()
    log = log.strip('\n\x1e').split("\x1e")
    log = (row.strip().split("\x1f") for row in log)
    log = (dict(zip(git_commit_fields, row)) for row in log)

    # Now we need to count the number of line additions and deletions are
    # associated with a particular bug. To do this we will check the commit message
    bug_msg = re.compile("(?P<bug_word>bug|bugs|fix|fixed|fixes|fix\s+for|fixes\s+for|defects|patch)",
                         re.IGNORECASE | re.MULTILINE)
    bug_ln_counts = re.compile("((?P<insertions>\d+) insertion).*((?P<deletions>\d+) deletion)",
                               re.IGNORECASE | re.MULTILINE)
    count_add = 0
    count_minus = 0

    added_content = []
    removed_content = []

    for row in log:
        m1 = bug_msg.search(row['message_header'])
        m2 = bug_msg.search(row['message_body'])
        if not m1 and not m2:
            pass
        else:
            # If we are here then we have a match for a bug. We need to extract the
            # number of additions and deletions
            m = bug_ln_counts.search(row['extra'])
            if m:
                count_add += int(m.group('insertions'))
                count_minus += int(m.group('deletions'))

                lines = row['extra'].split("\n")
                for line in lines:
                    if line.startswith("+ "):
                        added_content.append(line[1:])
                    elif line.startswith("- "):
                        removed_content.append(line[1:])
                    else:
                        pass
                added_content.clear()
                removed_content.clear()

    repo_content = (filename, count_add, count_minus)
    print(repo_content)
    return repo_content


def cd(repo_url):
    dir_name = ntpath.basename(repo_url)[:-4]
    if not os.path.exists(dir_name):
        # We need to clone the repo
        try:
            subprocess.check_output(['git', 'clone', repo_url])
        except subprocess.CalledProcessError:
            print("Unable to clone git repo")
            exit(0)
    os.chdir(dir_name)
    return dir_name


if __name__ == '__main__':
    main()
    # get_repo_data('https://github.com/ovitas/compass2.git')
