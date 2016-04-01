require(plyr)

rq1df = 14.74541
rq2df = 15.74213

calcEPV <- function(data) {

	names <- unique(data$name)
	names <- names[order(names)]

	vals <<- data.frame(names)
	vals[, 'rq1df'] <<- NA
	vals[, 'rq2df'] <<- NA

	rtn <- ddply(data, "name", function(subset) {
		curName <<- as.character(subset$name[1])

		numBuggy <- nrow(subset[which(subset$contains_bug == 't'),])

		vals[which(vals$name == curName), 'rq1df'] <<- numBuggy / rq1df
		vals[which(vals$name == curName), 'rq2df'] <<- numBuggy / rq2df

		return(vals)

	}, .progress = "text")

	vals <<- vals[which(vals$rq1df < 10 && vals$rq2df < 10),]

	return(vals)
}