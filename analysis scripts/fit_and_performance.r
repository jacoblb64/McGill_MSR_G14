require(rms)
require(plyr)
source('analysis scripts/performance.r')

# Configuration settings
metrics = c("classification", "ns", "nd", "nf", "entrophy", "la", "ld", "lt", "ndev", "age", "nuc", "exp", "rexp", "sexp")
rq1 = "commit_words"
rq2 = "bayesian_score"
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
  rq = "rq"
  if (myvar	== rq2) {
  	met <- append(metrics, rq1)
  	met <- append(met, rq2)
  	rq = "rq2"
  } else {
    met <- append(metrics, myvar)
    rq = "rq1"
  }

  # create blank data frames for AUC and Brier
  names <- unique(data$name)
  names <- names[order(names)]
  aucTable <<- data.frame(names)
  names(aucTable) = "name"

  for(name in names) {
  	aucTable[, name] <<- NA
  }

  brierTable <<- aucTable


  rtn <- ddply(data, "name",
    function(mydata) {
  	  curName <<- as.character(mydata$name[1])

      print(paste("Evaluating", curName, sep=" "))

      auc <- NA
      brier <- NA
      dropVal <- NA
      dropPVal <- NA

      # add new column to the tables
      # aucTable[, curName] <<- NA
      # brierTable[, curName] <<- NA

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
          # a <- anova(fit)
          # dropVal <- NA
          # dropPVal <- NA

          ## New Analysis

          # self-analysis
          aucTable[which(aucTable$name == curName), curName] <<- auc
          brierTable[which(aucTable$name == curName), curName] <<- brier
          
          # cross-analysis
          test <- ddply(data, "name", function(testdata) {
          	testName <<- as.character(testdata$name[1])

          	if (testName == curName) {
          		return(NA)
          	}

          	print(paste("    ", "Testing on", testName, sep=" "))
          	summary(testdata)

          	tryCatch({
          		colnames(testdata)[which(names(testdata) == "contains_bug")] <- "buggy"
          		testauc <- performance.auc(fit, testdata)
          		testbrier <- performance.brier(fit, testdata)
          		print(paste("values for", curName, testauc, testbrier, sep=" "))

          	# write new data to the right place
          	# ROW: training project
          	# Column: testing project
			aucTable[which(aucTable$name == curName), testName] <<- testauc
          	brierTable[which(aucTable$name == curName), testName] <<- testbrier

          	}, error = function(e) {
          		print(paste("Test Failed on", testName, sep=" "))
        	})

          	return(NA)

          })



          # if (myvar %in% cleanMetrics) {
          #   dropVal <- a[myvar,1]/a["TOTAL",impactMeasure]
          #   dropPVal <- a[myvar,"P"]
          # }
        }, error = function(e) {
          print(paste("FIT FAILED: SKIPPING", mydata$name[1], sep=" "))
        })
      } else {
      	print(paste("data not OK for fit, skipping"))
      }
        
      return(NA)
      # return(c(auc, brier, dropVal, dropPVal))
    })

  # names(rtn) <- c("proj", "AUC", "Brier", "Chi", "Pval")

  write.csv(aucTable, paste("data", "new", rq, "aucTable.csv", sep="/"))
  write.csv(brierTable, paste("data", "new", rq, "brierTable.csv", sep="/"))

  return(aucTable)
}

testFunction <- function() {
	testFrame = data.frame(c(3, 4))
	testFrame2 = data.frame(c(6, 7))
	test2 <- function() {
		testFrame[, 'new'] <<- 0
		print(testFrame)
	}
	test2()
	# write.csv(testFrame, 'testFrame.csv')
	# write.csv(testFrame2, 'testFrame2.csv')
	return(testFrame)
}
