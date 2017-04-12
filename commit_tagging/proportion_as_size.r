proportionAsSize <- function(data) {

	results <- data.frame(matrix(ncol = 3, nrow = 0))
	names(results) <- c("commit_words", "jacob", "charles")

	for (i in 1:max(data$commit_words)) {
		jacobT = nrow(subset(data, commit_words == i & jacob == "True"))
		jacobF = nrow(subset(data, commit_words == i & jacob == "False"))
		charlesT = nrow(subset(data, commit_words == i & charles == "True"))
		charlesF = nrow(subset(data, commit_words == i & jacob == "False"))

		perJacob <- jacobT / (jacobT + jacobF)
		perCharles <- charlesT / (charlesT + charlesF)
		row <- c(i, perJacob, perCharles)
		names(row) <- c("commit_words", "jacob", "charles")

		results <- rbind(results, row)
	}

	return(results)
}

proportionAsSize2 <- function(data) {

	results <- data.frame(matrix(ncol = 3, nrow = 0))
	names(results) <- c("lt", "jacob", "charles")

	for (i in 1:700) {
		jacobT = nrow(subset(data, lt == i & jacob == "True"))
		jacobF = nrow(subset(data, lt == i & jacob == "False"))
		charlesT = nrow(subset(data, lt == i & charles == "True"))
		charlesF = nrow(subset(data, lt == i & jacob == "False"))

		perJacob <- jacobT / (jacobT + jacobF)
		perCharles <- charlesT / (charlesT + charlesF)
		row <- c(i, perJacob, perCharles)
		names(row) <- c("lt", "jacob", "charles")

		results <- rbind(results, row)
	}

	return(results)
}