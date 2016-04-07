require(rms)
require(plyr)

# Configuration settings
# metrics = c("classification", "ns", "nd", "nf", "entrophy", "la", "ld", "lt", "ndev", "age", "nuc", "exp", "rexp", "sexp")
# switching to "fix" instead of "classification"
metrics = c("fix", "ns", "nd", "nf", "entrophy", "la", "ld", "lt", "ndev", "age", "nuc", "exp", "rexp", "sexp")
rq1 = "commit_words"
rq2 = "bayesian_score"
none = ""
depVar <- "contains_bug"
boots = 100
impactMeasure <- "Chi-Square"
eventThresh <- 20
penaltySetting <- 2

getCleanMetrics <- function(met, data) {
  form <- paste("~", paste(met, collapse=" + "), sep=" ")
  r <- redun(as.formula(form), data=data, nk=0)

  return(r$In)
}

subsetOkForFit <- function(data) {
  return (length(subset(data, contains_bug)$contains_bug) > 0 &
          length(subset(data, !contains_bug)$contains_bug) > 0 &
          length(subset(data, contains_bug)$contains_bug) >= eventThresh
          )
}

runExperiment <- function(data, metrics, myvar) {
  
  # including rq1 into the analysis of rq2
  rq = "rq"
  if (myvar == rq2) {
    met <- append(metrics, rq1)
    met <- append(met, rq2)
    rq = "rq2"
  } else if (myvar == none) {
    met <- metrics
    rq <- "baseline"
  } else {
    met <- append(metrics, myvar)
    rq = "rq1"
  }

  # testing explanatory power of classification
  # myvar <- "classification"

  rtn <- ddply(data, "name",
    function(mydata) {
      print(mydata$name[1])

      auc <- NA
      brier <- NA
      dropVal <- NA
      dropPVal <- NA

      if (subsetOkForFit(mydata)) {
        cleanMetrics <- getCleanMetrics(met, mydata)
        form <- paste(depVar, paste(cleanMetrics, collapse=" + "), sep = " ~ ")
        tryCatch({
          fit <- lrm(as.formula(form), data=mydata, x=T, y=T, penalty=penaltySetting)

          # Validation results
          v <- validate(fit, B=boots)
          auc <- v[1,5]/2+0.5
          brier <- v[9,5]

          # Impact analysis
          a <- anova(fit)
          dropVal <- NA
          dropPVal <- NA
          if (myvar %in% cleanMetrics) {
            dropVal <- a[myvar,1]/a["TOTAL",impactMeasure]
            dropPVal <- a[myvar,"P"]
          }
        }, error = function(e) {
          print(paste("FIT FAILED: SKIPPING", mydata$name[1], sep=" "))
        })
      }
        
      return(c(auc, brier, dropVal, dropPVal))
    }, .progress = "text")

  names(rtn) <- c("proj", "AUC", "Brier", "Chi", "Pval")

  return(rtn)
}
