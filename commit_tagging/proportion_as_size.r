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

numVagueAtSize <- function(data) {

	results <- data.frame(matrix(ncol = 5, nrow = 0))
	names(results) <- c("lt", "jacobT", "charlesT", "jacobF", "charlesF")

	for (i in 1:700) {
		jacobT <- nrow(subset(data, lt == i & jacob == "True"))
		jacobF <- nrow(subset(data, lt == i & jacob == "False"))
		charlesT <- nrow(subset(data, lt == i & charles == "True"))
		charlesF <- nrow(subset(data, lt == i & jacob == "False"))

		row <- c(i, jacobT, charlesT, jacobF, charlesF)
		names(row) <- c("lt", "jacobT", "charlesT", "jacobF", "charlesF")

		results <- rbind(results, row)
	}

	return(results)
}

proportionAsSizeBucketed <- function(data, bucketSize) {

	numVague <- numVagueAtSize(data)
	names(numVague) <- c("lt", "jacobT", "charlesT", "jacobF", "charlesF")

	# results <- data.frame(matrix(ncol = 3, nrow = 0))
	# names(results) <- c("lt", "jacob", "charles")
	# results$lt <- as.character(results$lt)
	# results$jacob <- as.numeric(results$jacob)
	# results$charles <- as.numeric(results$charles)

	results <- data.frame(lt=character(), jacob=numeric(), charles=numeric())
	results$lt <- as.character(results$lt)

	numBuckets <- ceiling(700 / bucketSize)
	curBucket <- bucketSize

	for (i in 1:numBuckets) {
		curBucket <- i*bucketSize
		lastBucket <- curBucket - bucketSize
		curSums <- colSums(subset(numVague, lt > lastBucket & lt <= curBucket))

		perJacob <- curSums["jacobT"] / (curSums["jacobT"] + curSums["jacobF"])
		perCharles <- curSums["charlesT"] / (curSums["charlesT"] + curSums["charlesF"])

		bucketName <- paste(lastBucket + 1, "-", curBucket, sep="")

		# row <- c(as.character(bucketName), as.numeric(perJacob), as.numeric(perCharles))
		# names(row) <- c("lt", "jacob", "charles")

		# results <- rbind(results, row)
		results[nrow(results)+1,] <- c(as.character(bucketName), as.numeric(perJacob), as.numeric(perCharles))
	}

	return(results)
}

plotProportionAsSizeBucketed <- function(results, person) {
	results$lt <- factor(results$lt, levels = results$lt)
	results$jacob <- as.numeric(results$jacob)
	results$charles <- as.numeric(results$charles)
	if (person == "jacob") {
		plot <- ggplot(results, aes(lt, jacob)) + geom_bar(stat="identity")
	}
	else {
		plot <- ggplot(results, aes(lt, charles)) + geom_bar(stat="identity")
	}

	return(plot)
}

plotWholeShebang <- function(data, bucketSize, person) {
	return(plotProportionAsSizeBucketed(proportionAsSizeBucketed(data, bucketSize), person))
}