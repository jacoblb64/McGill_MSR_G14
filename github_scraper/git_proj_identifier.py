import argparse
import csv
import ntpath
import sys
import re
import urllib.request
import time

from github import Github
from html.parser import HTMLParser

maxInt = sys.maxsize
decrement = True

pattern = re.compile('android', re.MULTILINE | re.IGNORECASE)

current_project_mapping = dict()
is_android = False

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


def main():
    global is_android
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', type=str, metavar='username', dest='username', required=True,
                        help='Username of your Github account')
    parser.add_argument('-p', '--password', type=str, metavar='password', dest='password', required=True,
                        help='Password of your Github account')
    data_input = parser.add_mutually_exclusive_group(required=True)
    data_input.add_argument('-f', '--filename', type=str, metavar='filename', dest='filename',
                            help='The .csv file containing the project names to identify')
    data_input.add_argument('-r', '--repositories', type=str, nargs='+',
                            help='A list of repository names to identify')
    args = parser.parse_args()

    if args.filename:
        print('Using filename {} as input for data'.format(args.filename))
        repositories = get_repo_urls_from_file(args.filename)
    else:
        print('Using repo list {} as input for data'.format(','.join(args.repositories)))
        repositories = args.repositories

    # repositories = ['https://github.com/eclipse/dltk.core.git']
    repo_mappings = get_repo_name_mapping(repositories)
    g = Github(args.username, args.password)

    for mapping in repo_mappings:
        print(mapping['repo_name'])
        print(mapping['repo_user'])
        repository = g.search_repositories(mapping['repo_name'] + 'in:name', user=mapping['repo_user'])[0]
        if mapping['repo_name'] not in current_project_mapping:
            current_project_mapping[mapping['repo_name']] = False
        # We have the repository
        print(repository.description)
        if repository.description and re.search(pattern, repository.description):
            current_project_mapping[mapping['repo_name']] = True
            print('Android in description')
        else:
            readme = repository.get_readme()
            if readme:
                readme_url = readme.html_url
                with urllib.request.urlopen(readme_url) as response:
                    readme_file = response.read().decode('utf-8')
                    htmlp = MyHTMLParser()
                    htmlp.feed(readme_file)
                if is_android:
                    current_project_mapping[mapping['repo_name']] = True
                    is_android = False
            if not readme or is_android is False:
                # We need to check the code
                code = g.search_code('android in:file', repo=mapping['repo_user'] + '/' + mapping['repo_name'])
                code_count = code.totalCount
                print('Search results from code : {}'.format(code_count))
                if code_count is not None and code_count:
                    current_project_mapping[mapping['repo_name']] = True
                    print('Found Android in code')
        time.sleep(10)
    else:
        with open('android_results.csv', mode='w', newline='') as dest_file:
            csv_writer = csv.DictWriter(dest_file, ['name', 'isAndroid'])
            csv_writer.writeheader()
            for project in current_project_mapping:
                csv_writer.writerow({'name': project, 'isAndroid': current_project_mapping[project]})


def get_repo_name_mapping(repo_urls):
    mappings = []
    for repo_url in repo_urls:
        if str(repo_url).endswith('.git'):
            repo_name = ntpath.basename(repo_url)[:-4]
        else:
            repo_name = ntpath.basename(repo_url)
        user_name = ntpath.basename(ntpath.dirname(repo_url))
        mapping = {'repo_user': user_name, 'repo_name': repo_name}
        mappings.append(mapping)
    return mappings


def get_repo_urls_from_file(filename):
    project_urls = set()
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for commit in csv_reader:
            project_urls.add(commit['url'])
    return project_urls


class MyHTMLParser(HTMLParser):

    def error(self, message):
        pass

    def handle_data(self, data):
        global is_android
        if re.search(pattern, data):
            is_android = True
            print('Android')


if __name__ == '__main__':
    main()
