For performing analysis:

1. Load R from the root repository directory
2. Import the new data set:
	data = read.csv('path/to/data.csv')
3. Convert the contains_bug column to logical
	data$contains_bug = data$contains_bug == 't'
3. Load the script
	source('analysis scripts/fit_and_performance.r')
4. Run the experiment for the rq and bounds desired
	runExperiment(data, metrics, rqX, Y, Z)
	where X is the rq#, Y is the start index, and Z is end index, inclusive
	e.g.: runExperiment(data, metrics, rq1, 1, 3) for the first 3 projects



For merging the data together:

1. Load all data sets into variables
2. Data can be merged with rbind(set1, set2)
3. Before saving:
	- rename any column names that were prefixed with 'X'
		names$data[index_of_name_with_X] <- "name_without_X"
	- remove the 'X' column
		data$X <- NULL
4. Save the merged csv
	write.csv(data, 'path/to/data.csv')
	e.g.: write.csv(data, 'data/new/rq1/aucTable1-20.csv')


- Try to maintain the naming convention of aucTable and brierTable,
  with the suffixes for the projects included

- don't save R workspace image upon exiting, as .Rdata will be massive
  instead, use the savehistory() command before exiting

- check .Rdata for examples and a history of execution if you have
  any questions

IMPORTANT:
- Upload to Git after every run! So everyone can see what has already been
  analyzed and what hasn't! Pull before pushing though!

- Choose appropriate sized chunks to analyze at a time. I recommend starting
  with a couple projects, no more than 3 to begin, which should take ~10 mins,
  from there, you can calculate how long a set number of projects take

- Indicies are inclusive, so start at the number after the last one left off

- Packages might have to be downloaded prior to running, use the command
  install.packages('package_to_be_downloaded')
  and follow the onscreen instructions
  e.g.: install.packages('rms')