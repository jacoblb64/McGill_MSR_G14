require(ggplot2)

auc = "Auc"
brier = "Brier"
rq1 = "rq1"
rq2 = "rq2"

proj = "proj"
modelType = "model_type"
chi = "Chi"
name = "name"
mag = "cdMag"

# plot the predict performance of one metric / rq DEPRECATED
plotPerformance <- function(table, metric, rq) {

	# reorder factor levels for consistent plotting
	table$cdMag <- factor(table$cdMag, levels = c("negligible", "small", "medium", "large"))

	# full plot
	plot <- ggplot(table[ which(!(is.na(table$wilcoxP))),], aes(cdMag))
	plot <- plot + geom_bar()
	plot <- plot + labs(x="Magnitude", y = "Projects", title=paste(metric, "scores for", toupper(rq), "(Full)"))
	ggsave(paste('data/new/', rq, '/', metric, 'Full.pdf', sep=""), plot = plot)

	# subset plot, significant projects
	alpha <- nrow(table) - nrow(table[ which(is.na(table$wilcoxP)),])
	plot <- ggplot(table[ which(table$wilcoxP < 0.05 / alpha),], aes(cdMag))
	plot <- plot + geom_bar()
	plot <- plot + labs(x="Magnitude", y = "Projects", title=paste(metric, "scores for", toupper(rq), "(Significant)"))
	ggsave(paste('data/new/', rq, '/', metric, 'Sig.pdf', sep=""), plot = plot)
}

# plot all the performances of predictions
plotAllPerformance <- function(auc1, auc2, brier1, brier2) {

	auc1 <- appendRq( cleanMetricSet( subsetSignificant(auc1)[, c(name, mag)], toupper(auc) ), rq1 )
	auc2 <- appendRq( cleanMetricSet( subsetSignificant(auc2)[, c(name, mag)], toupper(auc) ), rq2 )

	brier1 <- appendRq( cleanMetricSet( subsetSignificant(brier1)[, c(name, mag)], brier ), rq1 )
	brier2 <- appendRq( cleanMetricSet( subsetSignificant(brier2)[, c(name, mag)], brier ), rq2 )
	
	# For RQ1
	bar <- rbind(auc1, brier1)
	bar[,'metric'] <- factor(bar[,'metric'], levels = c("Brier", "AUC"))
	bar[,'value'] <- factor(bar[,'value'], levels = c("negligible", "small", "medium", "large"))

	plot <- ggplot(bar, aes(metric))
	plot <- plot + geom_bar(aes(fill = value), position = "fill")
	plot <- plot + coord_flip() + theme_bw() +  scale_fill_grey( start = 0.9, end = 0.1, name = "Cliff's Delta")
	plot <- plot + ylab("Percentage of Projects") + xlab("Commit Volume")
	plot <- plot + scale_y_continuous(labels = scales::percent)

	ggsave("data/new/predictive1.pdf", width=5, height=2)

	# For RQ2
	bar <- rbind(auc2, brier2)
	bar[,'metric'] <- factor(bar[,'metric'], levels = c("Brier", "AUC"))
	bar[,'value'] <- factor(bar[,'value'], levels = c("negligible", "small", "medium", "large"))

	plot <- ggplot(bar, aes(metric))
	plot <- plot + geom_bar(aes(fill = value), position = "fill")
	plot <- plot + coord_flip() + theme_bw() +  scale_fill_grey( start = 0.9, end = 0.1, name = "Cliff's Delta")
	plot <- plot + ylab("Percentage of Projects") + xlab("Commit Content")
	plot <- plot + scale_y_continuous(labels = scales::percent)

	ggsave("data/new/predictive2.pdf", width=5, height=2)
}

plotMedianPerformance <- function(auc1, auc2, brier1, brier2) {

	# Auc score presented as AUC
	auc <- toupper(auc)

	# prepare to make the first plot
	auc1 <- appendRq( cleanMetricSet( rowMedians(auc1, auc), auc ), rq1 )
	auc2 <- appendRq( cleanMetricSet( rowMedians(auc2, auc), auc ), rq2 )

	brier1 <- appendRq( cleanMetricSet( rowMedians(brier1, brier), brier ), rq1 )
	brier2 <- appendRq( cleanMetricSet( rowMedians(brier2, brier), brier ), rq2 )

	# Performance plot
	box <- rbind(auc1, auc2, brier1, brier2)

	plot <- ggplot(box, aes(metric, value, fill=model_type))
	plot <- plot + geom_boxplot() + theme_bw()
	plot <- plot + scale_fill_grey(start=0.5, name = "Model Type")+ ylim(c(0,1))
	plot <- plot + ylab("Value") + theme(axis.title.x = element_blank(), legend.position=c(0.85, 0.85))

	ggsave("data/new/performanceP.pdf", width=5, height=4)
}

# generate box plots for explanatory analysis
expBoxPlot <- function(exp1, exp2) {

	# Auc score presented as AUC
	auc <- toupper(auc)

	# prepare to make the first plot
	auc1 <- appendRq( cleanMetricSet( exp1[, c(proj, auc)], auc ), rq1 )
	auc2 <- appendRq( cleanMetricSet( exp2[, c(proj, auc)], auc ), rq2 )

	brier1 <- appendRq( cleanMetricSet( exp1[, c(proj, brier)], brier ), rq1 )
	brier2 <- appendRq( cleanMetricSet( exp2[, c(proj, brier)], brier ), rq2 )

	# Performance plot
	box <- rbind(auc1, auc2, brier1, brier2)

	plot <- ggplot(box, aes(metric, value, fill=model_type))
	plot <- plot + geom_boxplot() + theme_bw()
	plot <- plot + scale_fill_grey(start=0.5, name = "Model Type")
	plot <- plot + ylab("Value") + theme(axis.title.x = element_blank(), legend.position=c(0.85, 0.85))

	ggsave("data/new/performance.pdf", width=5, height=4)

	# prepare to make the second plot
	chi1 <- appendRq( cleanMetricSet( exp1[, c(proj, chi)], chi ), rq1 )
	chi2 <- appendRq( cleanMetricSet( exp2[, c(proj, chi)], chi ), rq2 )

	# box <- rbind(chi1, chi2)

	# For RQ1
	plot <- ggplot(chi1, aes(model_type, value, fill=model_type))
	plot <- plot + geom_boxplot()+ theme_bw()
	plot <- plot + ylab("Percentage of explanatory power")
	plot <- plot + theme(axis.title.x = element_blank(), legend.position = "none")
	plot <- plot + scale_y_continuous(labels = scales::percent, limits = c(0, 0.9)) + scale_fill_grey(start=0.4)

	ggsave("data/new/expl_power1.pdf", width=2, height=4)

	# For RQ2
	plot <- ggplot(chi2, aes(model_type, value, fill=model_type))
	plot <- plot + geom_boxplot()+ theme_bw()
	plot <- plot + ylab("Percentage of explanatory power")
	plot <- plot + theme(axis.title.x = element_blank(), legend.position = "none")
	plot <- plot + scale_y_continuous(labels = scales::percent, limits = c(0, 0.9)) + scale_fill_grey(start=0.8)

	ggsave("data/new/expl_power2.pdf", width=2, height=4)
}

rowMedians <- function(table, metric) {
	rtn <- data.frame(table$name)
	table$X <- NULL

	table <- apply(table, 1, function(row) {
		rtn[row[1], metric] <<- median(as.numeric(row[2:length(row)]), na.rm=T)
	})
	names(rtn)[1] <- 'proj'

	return(rtn)
}

subsetSignificant <- function(table) {
	return(table[ which(table$wilcoxP < 0.001 / nrow(table)),])
}


cleanMetricSet <- function(table, metric) {
	names(table)[2] <- 'value'
	table[, 'metric'] <- metric

	return(table)
}

appendRq <- function(table, rq) {
	table[, modelType] <- rqToWords(rq)

	table[, modelType] <- as.factor(table[, modelType])

	return(table)
}

rqToWords <- function(rq) {
		if (rq == rq1) {
		return("Volume")
	}
	else if (rq == rq2) {
		return("Content")
	}
}