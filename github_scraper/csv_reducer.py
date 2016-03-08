import sys
import csv

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


def commits_count():
    csv_path = sys.argv[1]

    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        app = {}
        for commit in csv_reader:
            if commit['name'] not in app:
                app[commit['name']] = 1
            else:
                app[commit['name']] += 1
        with open('cpp.txt', mode='w') as outfile:
            for project in sort_dict_by_key(app):
                if app[project] < 700:
                    print(project + " " + str(app[project]) + "\n")
                outfile.write(project + " " + str(app[project]) + "\n")


def author_count():
    csv_path = sys.argv[1]

    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        app = {}
        for commit in csv_reader:
            if commit['name'] not in app:
                app[commit['name']] = set()
                app[commit['name']].add(commit['author_name'])
            else:
                app[commit['name']].add(commit['author_name'])
        with open('app.txt', mode='w') as outfile:
            for project in sort_dict_by_key(app):
                if len(app[project]) < 10:
                    print(project + " " + str(len(app[project])) + "\n")
                outfile.write(project + " " + str(len(app[project])) + "\n")


def sort_dict_by_key(data: dict):
    return sorted(list(data), key=str.lower)


def main():
    csv_path = sys.argv[1]

    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        fieldnames = csv_reader.fieldnames
        unwanted = ['commit_hash', 'commit_message']
        fieldnames = [name for name in fieldnames if name not in unwanted]
        with open('reduced.csv', mode='w', newline='') as csv_out:
            csv_writer = csv.DictWriter(csv_out, fieldnames)
            csv_writer.writeheader()
            for commit in csv_reader:
                commit = {k: commit[k] for k in commit if k not in unwanted}
                csv_writer.writerow(dict(commit))

if __name__ == '__main__':
    # main()
    # author_count()
    commits_count()
