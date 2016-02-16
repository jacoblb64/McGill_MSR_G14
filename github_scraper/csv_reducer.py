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
    main()
