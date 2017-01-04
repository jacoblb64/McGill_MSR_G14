#! /usr/bin/env python

import csv
import argparse



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--filename', dest='csv_path', required=True, metavar='data.csv',
						type=str, help='csv file including path')
	args = parser.parse_args()
	csv_path = args.csv_path

	person = input("Who is tagging?\n").lower()
	if person != "charles" and person != "jacob":
		print("not a valid person")
		return

	with open(csv_path, 'r', errors='ignore') as csvfile:
		reader = csv.DictReader(csvfile)
		with open(person + "_out.csv", 'a') as outfile:
			fieldnames = reader.fieldnames
			if person not in fieldnames:
				fieldnames.append(person)
			writer = csv.DictWriter(outfile, fieldnames)

			count = 0
			try:
				with open(person + "count.txt", 'r') as countfile:
					count = int(next(countfile))
				print("resuming from index " + str(count + 1))
			except FileNotFoundError:
				print("starting from the beginning")
				writer.writeheader()



			for i, row in enumerate(reader):
				if i < count:
					continue
				print(row['commit_message'])
				isVague = input("Is this vague? (y/n)\n")
				isVague = str_to_bool(isVague)
				row.update({person: isVague})
				writer.writerow(row)

				with open(person + "count.txt", 'w') as countfile:
					countfile.write(str(i))


def str_to_bool(s):
	if s in ['y', 'Y']:
		 return True
	elif s in ['n', 'N']:
		 return False
	else:
		 raise ValueError # evil ValueError that doesn't tell you what the wrong value was


if __name__ == "__main__":
	main()