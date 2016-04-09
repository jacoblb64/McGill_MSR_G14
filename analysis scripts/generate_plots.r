require(ggplot2)

auc = "Auc"
brier = "Brier"
rq1 = "rq1"
rq2 = "rq2"

proj = "proj"
modelType = "model_type"
chi = "Chi"

plotPerformance <- function(table, metric, rq) {

	# reorder factor levels for consistent plotting
	table$cdMag <- factor(table$cdMag, levels = c("negligible", "small", "medium", "large"))

	# full plot
	plot <- ggplot(table[ which(!(is.na(table$wilcoxP))),], aes(cdMag))
	plot <- plot + geom_bar()
	plot <- plot + labs(x="Magnitude", y = "Projects", title=paste(metric, "scores for", toupper(rq), "(Full)"))
	ggsave(paste('data/new/', rq, '/', metric, 'Full.pdf', sep=""), plot = plot)

	# subset plot, significant projects
	alpha = nrow(table) - nrow(table[ which(is.na(table$wilcoxP)),])
	plot <- ggplot(table[ which(table$wilcoxP < 0.05 / alpha),], aes(cdMag))
	plot <- plot + geom_bar()
	plot <- plot + labs(x="Magnitude", y = "Projects", title=paste(metric, "scores for", toupper(rq), "(Significant)"))
	ggsave(paste('data/new/', rq, '/', metric, 'Sig.pdf', sep=""), plot = plot)
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

	box <- rbind(auc1, auc2, brier1, brier2)

	plot <- ggplot(box, aes(metric, value, fill=model_type))
	plot <- plot + geom_boxplot() + theme_bw()
	plot <- plot + scale_fill_grey(start=0.5, name = "Model Type")
	plot <- plot + ylab("Value") + theme(axis.title.x = element_blank(), legend.position=c(0.85, 0.85))

	ggsave("data/new/performance.pdf", width=5, height=4)


	# prepare to make the second plot
	chi1 <- appendRq( cleanMetricSet( exp1[, c(proj, chi)], chi ), rq1 )
	chi2 <- appendRq( cleanMetricSet( exp2[, c(proj, chi)], chi ), rq2 )

	box <- rbind(chi1, chi2)

	plot <- ggplot(box, aes(model_type, value, fill=model_type))
	plot <- plot + geom_boxplot()+ theme_bw()
	plot <- plot + ylab("Percentage of explanatory power")
	plot <- plot + theme(axis.title.x = element_blank(), legend.position = "none")
	plot <- plot + scale_y_continuous(labels = scales::percent) + scale_fill_grey(start=0.4)

	ggsave("data/new/expl_power.pdf", width=5, height=4)
}

cleanMetricSet <- function(table, metric) {
	names(table)[2] <- 'value'
	table[, 'metric'] <- metric

	return(table)
}

appendRq <- function(table, rq) {
	if (rq == rq1) {
		table[, modelType] <- "Volume"
	}
	else if (rq == rq2) {
		table[, modelType] <- "Content"
	}

	table[, modelType] <- as.factor(table[, modelType])

	return(table)
}