require(taRifx)

# removes metadata and converts all data to numerical
cleanTable <- function(table) {
  table$X <- NULL
  table$name <- NULL
  # table <- japply( table, which(sapply(table, class)=="logical"), as.numeric )

  table <- table[rowSums(is.na(table))<1200,]

  return(table)
}

process <- function(performance_with, performance_wo) {

  name <- performance_with$name

  performance_with <- cleanTable(performance_with)
  performance_wo <- cleanTable(performance_wo)

  # withMeans = rowMeans(performance_with, na.rm = TRUE, dims = 1)
  # woMeans = rowMeans(performance_wo, na.rm = TRUE, dims = 1)

  results <- data.frame(name)
  results[,'Pwilcox'] <- NA

  width <- length(names(performance_with))

  pb <- txtProgressBar(min = 0, max = width, style = 3)

  for (i in 1:width) {

    if (!is.na(performance_with[i,3]) && !is.na(performance_wo[i,3])) {
      wilcox <- wilcox.test(as.numeric(performance_with[i,]),
                          as.numeric(performance_wo[i,]),
                          na.action=na.exclude)
      results[i, 'Pwilcox'] <- as.numeric(wilcox[['p.value']])
    } else {
      results[i, 'Pwilcox'] <- NA
    }

    setTxtProgressBar(pb, i)
  }

  return(results)
}