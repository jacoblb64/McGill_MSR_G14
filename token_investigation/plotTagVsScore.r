require(ggplot2)

plotTagVsScore <- function(table, writename) {
	plot <- ggplot(table, aes(POS, score))
	plot <- plot + geom_boxplot()
	ggsave(paste(writename, ".pdf", sep=""), width=10, height=4)
}

plotWordVsScore <- function(table, writename) {
	plot <- ggplot(table, aes(word, score))
	plot <- plot + geom_boxplot()
	ggsave(paste(writename, ".pdf", sep=""), width=10, height=4)
}

generateKneeTable <- function(table) {
	rtn <- data.frame("count" = 0, "freq" = 0)
	val <- NULL

	for (i in 1:20) {
		val <- nrow(subset(table, total == i))
		rtn <- rbind(rtn, c(i, val))
	}

	return(rtn)
}