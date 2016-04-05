badnames <- read.csv('data/new/33fail.csv')
badnamesdot <- apply(badnames, 1, function(row) gsub("-",".",row['x']))
badnames <- badnames[['x']]

removeProjects <- function(table) {
	# remove columns (in which "-" has been replaced with ".")
	for (name in badnamesdot) {
		table[name] <- NULL
	}

	# remove rows
	table <- table[ which(!(table$name %in% badnames)),]

	# clean junk columns
	table$X.1 <- NULL
	table$X <- NULL

	return(table)
}