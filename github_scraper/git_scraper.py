import subprocess
import os
import ntpath
import re

__author__ = 'Charles'


def main():
    # We need to get repo urls then we call call cd(repo_url)
    repo_url = "https://bitbucket.org/cgathuru/dnsclient.git"  # Using this as a dummy repo_url
    cd(repo_url)  # We will enable this when we have a repo to go through
    repository_info = []
    output = get_file_output(filename='test/dnsclient/DnsClientTest.java')


def get_file_output(filename):
    """
    :param filename: The filename to search for bugs
    :return: A triple in format $filename $added_lns $removed_lns representing the number of added lines
    and removed lines that have bug fixes in them
    """
    git_commit_fields = ['id', 'author_name', 'date', 'message_header', 'message_body', 'stat']
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
            m = bug_ln_counts.search(row['stat'])
            if m:
                count_add += int(m.group('insertions'))
                count_minus += int(m.group('deletions'))

                lines = row['stat'].split("\n")
                for line in lines:
                    if line.startswith("+ "):
                        added_content.append(line[1:])
                    elif line.startswith("- "):
                        removed_content.append(line[1:])
                    else:
                        pass

    repo_content = (filename, count_add, count_minus)
    print(repo_content)
    return removed_content


def cd(repo_url):
    dir_name = ntpath.basename(repo_url)[:-4]
    if not os.path.exists(dir_name):
        # We need to clone the repo
        try:
            subprocess.check_output(['git clone', repo_url])
        except subprocess.CalledProcessError:
            print("Unable to clone git repo")
            exit(0)
    os.chdir(dir_name)


if __name__ == '__main__':
    main()
