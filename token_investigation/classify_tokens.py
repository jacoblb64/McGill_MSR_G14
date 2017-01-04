#! /usr/bin/env python

from __future__ import generators

import os
import sys
import argparse
import csv
import re
from collections import defaultdict
import nltk
import enchant
from nltk.corpus import wordnet
import progressbar

nltk.data.path.append('/Users/Jacob/Documents/SDK/nltk')

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', dest='csv_path', required=True, metavar='data.csv',
                        type=str, help='csv file including path')
    args = parser.parse_args()
    csv_path = args.csv_path

    addPOS(csv_path)

def try1():
    with open("toksheadered1000.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for (k,v) in row.items():
                columns[k].append(v)

    # print(columns['token'])

    try:
        # for t in columns['token'][0:10]:
        tagged = nltk.pos_tag(columns['token'][0:10])
        print(tagged)
    except Exception as e:
        print(str(e))

def isEnglishWord(word):
    d = enchant.Dict("en_US")
    if (d.check(word)):
        return "word"

    if (len(d.suggest(word)) > 0):
        return "close"

    return "not"

def isLexical(word):
    synsets = wordnet.synsets(word)

    if len(synsets) > 0:
        return len(synsets)

    d = enchant.Dict("en_US")
    suggestions = d.suggest(word)
    if (len(suggestions) > 0):
        synsets = wordnet.synsets(suggestions[0])
        return len(synsets)

    return 0

def isInCorpus(word, corpus):
    if corpus == "vague":
        corpus_file = "vague_words.txt"
    elif corpus == "swears":
        corpus_file = "swear_words.txt"

    with open(corpus_file) as word_file:
        word_list = set(item.strip().lower() for item in word_file)

    word = word.lower()
    if word in word_list:
        return True

    # d = enchant.Dict("en_US")
    # suggestions = d.suggest(word)
    # if (len(suggestions) > 0):
    #     for sug in suggestions:
    #         if sug in word_list:
    #             return True

    return False


def addPOS(csv_path):
    # with open(csv_path, encoding='utf-8', errors='ignore') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         for (k,v) in row.items():
    #             columns[k].append(v)


    with open(csv_path, errors='ignore') as csvfile:
        reader = csv.DictReader(csvfile)
        with open('results.csv', mode='w') as csv_out:
            fieldnames = reader.fieldnames
            fieldnames.append('POS')
            fieldnames.append('word')
            fieldnames.append('lexical')
            # fieldnames.append('vague')
            # fieldnames.append('swear')
            writer = csv.DictWriter(csv_out, fieldnames)
            writer.writeheader()

            bar = progressbar.ProgressBar(redirect_stdout=True, max_value=progressbar.UnknownLength)

            for index, row in enumerate(reader):
                bar.update(index)

                pos = nltk.pos_tag([row['token']])
                row.update({"POS": pos[0][1]})

                word = isEnglishWord(row['token'])
                row.update({"word": word})

                lex = isLexical(row['token'])
                row.update({"lexical": lex})

                # vague = isInCorpus(row['token'], "vague")
                # row.update({"vague": vague})

                # swear = isInCorpus(row['token'], "swears")
                # row.update({"swear": swear})

                writer.writerow(row)


if __name__ == "__main__":
    main()