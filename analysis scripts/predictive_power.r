# require(taRifx)
require(effsize)
require(plyr)

auc = "auc"
brier = "brier"

wilcoxP = "wilcoxP"
cdEst = "cdEst"
cdMag = "cdMag"
newvars = c(wilcoxP, cdEst, cdMag)

# removes metadata and converts all data to numerical
cleanTable <- function(table) {

  table <- table[order(table$name)]

  table$X <- NULL
  # table$name <- NULL
  # table <- japply( table, which(sapply(table, class)=="logical"), as.numeric )

  # table <- table[rowSums(is.na(table))<1200,]

  return(table)
}

analyzePredictive <- function(performance_with, performance_wo, metric) {

  if (metric == auc) {
    comparison <- "greater"
  } else if (metric == brier) {
    comparison <- "less"
  }
  else {
    return("not valid input!")
  }

  name <- performance_with$name

  performance_with <- cleanTable(performance_with)
  performance_wo <- cleanTable(performance_wo)

  # withMeans = rowMeans(performance_with, na.rm = TRUE, dims = 1)
  # woMeans = rowMeans(performance_wo, na.rm = TRUE, dims = 1)

  results <- data.frame(name)
  for (var in newvars) {
    results[, var] <- NULL
  }

  width <- length(names(performance_wo)) - 1
  length <- nrow(performance_with)

  pb <- txtProgressBar(min = 0, max = width, style = 3)

  for (i in 1:length) {

    if (!is.na(performance_with[i,5]) && !is.na(performance_wo[i,5])
        && as.character(performance_with[i, 'name']) == as.character(performance_wo[i, 'name'])) {
      wilcox <- wilcox.test(as.numeric(performance_with[i,2:width]),
                          as.numeric(performance_wo[i,2:width]),
                          na.action=na.exclude, paired=T, alternative=comparison)
      results[i, wilcoxP] <- as.numeric(wilcox[['p.value']])

      cliffs <- cliff.delta(as.numeric(performance_with[i,2:width]),
                          as.numeric(performance_wo[i,2:width]),
                          na.action=na.exclude)
      results[i, cdEst] <- as.numeric(cliffs[['estimate']])
      results[i, cdMag] <- cliffs[['magnitude']]
    }

    setTxtProgressBar(pb, i)
  }

  # ddply(performance_with, "name", function(row) {
  #   curName <- as.character(row$name[1])
  #   row$name <- NULL

  #   wilcox <- wilcox.test(as.numeric(row),
  #                       as.numeric(performance_wo[ which(performance_wo$name == curName), names(performance_wo)[2:ncol(performance_wo)] ]),
  #                       na.action=na.exclude, paired=T, alternative=comparison)
  #   results[i, wilcoxP] <- as.numeric(wilcox[['p.value']])

  #   cliffs <- cliff.delta(as.numeric(row),
  #                       as.numeric(performance_wo[ which(performance_wo$name == curName), names(performance_wo)[2:ncol(performance_wo)] ]),
  #                       na.action=na.exclude)
  #   results[i, cdEst] <- as.numeric(cliffs[['estimate']])
  #   results[i, cdMag] <- cliffs[['magnitude']]
  # }, .progress = "text")

  return(results)
}

generateAllQuantiles <- function(auc1, auc2, brier1, brier2) {
  rtn <- data.frame(c("auc1", "auc2", "brier1", "brier2", "allauc", "allbrier"))
  names(rtn)[1] = "type"
  rtn[,"low"] <- NA
  rtn[, "high"] <- NA

  # allauc <- rbind(auc1, auc2)
  # allbrier <- rbind(brier1, brier2)

  rtn[which(rtn$type == 'auc1'),2:3] <- generateQuantiles(auc1)
  rtn[which(rtn$type == 'auc2'),2:3] <- generateQuantiles(auc2)
  rtn[which(rtn$type == 'brier1'),2:3] <- generateQuantiles(brier1)
  rtn[which(rtn$type == 'brier2'),2:3] <- generateQuantiles(brier2)
  rtn[which(rtn$type == 'allauc'),2:3] <- generateQuantilesFromTwo(auc1, auc2)
  rtn[which(rtn$type == 'allbrier'),2:3] <- generateQuantilesFromTwo(brier1, brier2)


  return(rtn)
}

# generates 3% and 97% quartiles
generateQuantiles <- function(table) {
  low = 0.25
  high = 0.975

  table$X <- NULL
  table$name <- NULL

  stack <- stack(table, names(table))

  return(c(quantile(stack$values, low, na.rm=T), quantile(stack$values, high, na.rm=T)))
}

# generates 3% and 97% quartiles
generateQuantilesFromTwo <- function(table1, table2) {
  low = 0.25
  high = 0.975

  table1$X <- NULL
  table1$name <- NULL
  table2$X <- NULL
  table2$name <- NULL

  stack1 <- stack(table1, names(table1))
  stack2 <- stack(table2, names(table2))

  stack <- rbind(stack1, stack2)

  return(c(quantile(stack$values, low, na.rm=T), quantile(stack$values, high, na.rm=T)))
}