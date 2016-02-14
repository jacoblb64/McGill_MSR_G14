#! /usr/bin/env python

from __future__ import generators

import os
import sys
import argparse
import csv
import re
from collections import defaultdict

sys.path.insert(-1, os.getcwd())
sys.path.insert(-1, os.path.dirname(os.getcwd()))

columns = defaultdict(list) # each value in each column is appended to a list


maxInt = sys.maxsize
decrement = True

while decrement:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt / 10)
        decrement = True

# http://stackoverflow.com/questions/16503560/read-specific-columns-from-csv-file-with-python-csv
def main():
    choose = 1

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', dest='csv_path', required=True, metavar='data.csv',
                        type=str, help='csv file including path')
    parser.add_argument('-c', '--choose', dest='choose', required=False, metavar='choose',
                        type=int, help='choose function')
    args = parser.parse_args()
    csv_path = args.csv_path
    choose = args.choose

    if choose == 2:
        fn2(csv_path)
        return
    if choose == 3:
        fn3(csv_path)
        return
    if choose == 4:
        remove_extraneous(csv_path)
        return

    print 'opening csv...'

    with open(csv_path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for (k,v) in row.items():
                columns[k].append(v)

    true_pattern = re.compile("^(?:)(true|t)$")
    false_pattern = re.compile("^(?:)(false|f)$")

    print 'organizing data into folders...'

    project_names = defaultdict(int)
    count = 0
    curname = "" # start blank
    setnum = 0
    setcount = 0
    for msg in columns['commit_message']:
        isbug = str.lower(columns['contains_bug'][count])
        if true_pattern.match(isbug):
            hsdir = "Spam"
        elif false_pattern.match(isbug):
            hsdir = "Ham"
        else:
            print 'undefined t/f for contains_bug!'
            return

        newname = columns['name'][count] # if repetition no need to look up
        if newname != curname:
            if newname in project_names:
                setnum = project_names[newname]
            else:
                setcount += 1
                setnum = setcount
                project_names[newname] = setnum

        print '#' + str(count) + ': placing ' + hsdir + ' commit from ' + newname + ' into set ' + str(setnum)

        dirname = "Data/" + str(hsdir) + "/Set" + str(setnum)

        if not os.path.exists(dirname):
            os.makedirs(dirname)
            print 'creating directory ' + str(dirname)

        # txtfile = open(dirname + "/" + columns['commit_hash'][count] + ".txt", "w")
        txtfile = open(dirname + "/" + str(count+1) + ".txt", "w")
        txtfile.write(msg)
        txtfile.close()
        curname = columns['name'][count]
        count += 1

    # create any directories that weren't created
    for num in range(1, setcount + 1):
        hamdir = "Data/Ham/Set" + str(num)
        spamdir = "Data/Spam/Set" + str(num)
        if not os.path.exists(hamdir):
            os.makedirs(hamdir)
            print 'creating directory ' + str(hamdir)
        if not os.path.exists(spamdir):
            os.makedirs(spamdir)
            print 'creating directory ' + str(spamdir)

    # write final count to file
    print 'created ' + str(setcount) + ' sets for testing'
    txtfile = open("numsets.txt", "w")
    txtfile.write(str(setcount) + "\n")
    txtfile.close()    

def fn2(csv_path): # taken from charles

    print 'creating final results...'

    sratios = defaultdict(list) # each value in each column is appended to a list

    with open("Data/sorted_ratios.csv", 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for (k,v) in row.items():
                sratios[k].append(v)

    with open(csv_path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open('results.csv', mode='w') as csv_file_out:
            fieldnames = csv_reader.fieldnames
            fieldnames.append('bayesian_score')
            fieldnames.append('spam_ham')
            writer = csv.DictWriter(csv_file_out, fieldnames)
            writer.writeheader()
            for index, commit in enumerate(csv_reader):
                # write new value to baysian_score
                bayesian_score = sratios['prob'][index]
                commit.update({'bayesian_score': bayesian_score})
                spam_ham = sratios['spamham'][index]
                commit.update({'spam_ham': spam_ham})
                writer.writerow(commit)
                # print(index)

def fn3(csv_path):
    print 'sorting...'
    reader = csv.DictReader(open(csv_path, 'r'))
    result = sorted(reader, key=lambda d: int(d['index']))

    writer = csv.DictWriter(open('Data/sorted_ratios.csv', 'w'), reader.fieldnames)
    writer.writeheader()
    writer.writerows(result)

# not working yet
def remove_extraneous(csv_path):
    with open(csv_path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open('results_lite.csv', mode='w') as csv_file_out:
            fieldnames = csv_reader.fieldnames

            # remove extraneous columns
            # fieldnames.remove('commit_hash')
            # fieldnames.remove('commit_message')

            unwanted = ['commit_hash', 'commit_message']

            writer = csv.DictWriter(csv_file_out, fieldnames, extrasaction='ignore')
            writer.writeheader()
            for index, commit in enumerate(csv_reader):
                commit = {k: commit[k] for k in commit if k not in unwanted}
                print index
                writer.writerow(commit)

    with open('results_lite.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open('results_lite2.csv', mode='w') as csv_file_out:
            fieldnames = csv_reader.fieldnames

            # remove extraneous columns
            fieldnames.remove('commit_hash')
            fieldnames.remove('commit_message')

            # unwanted = ['commit_hash', 'commit_message']

            writer = csv.DictWriter(csv_file_out, fieldnames, extrasaction='ignore')
            writer.writeheader()
            for index, commit in enumerate(csv_reader):
                # commit = {k: commit[k] for k in commit if k not in unwanted}
                print 'x2 ' + str(index)
                writer.writerow(commit)

if __name__ == "__main__":
    main()
    # dirname = "Ham/Set56"
    # if not os.path.exists(dirname):
    #     os.makedirs(dirname)
    #     print 'nooo'
    # else:
    #     print 'yoooo'