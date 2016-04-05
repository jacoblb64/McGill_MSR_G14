# badnames <- read.csv('data/new/33fail.csv')

# convert a list of row names to a list of column names
rowToTableNames <- function(badnames) {
	badnamescols <- apply(badnames, 1, function(row) {
		val <- gsub("-",".",row['x'])
		if (!is.na(as.numeric(substr(val, 1, 1)))) {
			# above line will throw warning for coersion
			val <- paste("X", val, sep="")
		}
		return(val)
	})
	return(badnamescols)
}

removeProjects <- function(table, badnames) {

	# get list of names to be removed, transforming for column "-" to "."
	badnamescols <- suppressWarnings(rowToTableNames(badnames))
	badnames <- badnames[['x']]

	# remove columns (in which "-" has been replaced with ".")
	for (name in badnamescols) {
		table[name] <- NULL
	}

	# remove rows
	table <- table[ which(!(table$name %in% badnames)),]

	# clean junk columns
	table$X.1 <- NULL
	table$X <- NULL

	return(table)
}