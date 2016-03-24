require(rms)
require(zoo) # For rollmean

pred.probs <- function(fit, data) {
  odds <- predict(fit, data)

  probs <- exp(odds)/(1+exp(odds))
  probs[is.na(probs)] <- 1 #HACK: NAs are treated as buggy

  return(probs)
}

performance.brier <- function(fit, data) {
  probs <- pred.probs(fit, data)
  resids <- ifelse(data$buggy == T, 1, 0)-probs
  return(sum(resids^2)/nrow(data))
}

areauc <- function(x, y) {
  return(sum(diff(x)*rollmean(y,2)))
}

performance.auc <- function(fit, data) {
  probs <- pred.probs(fit, data)

  tpr <- c()
  fpr <- c()
  for (thresh in seq(0,1,by=0.01)) {
    preds <- probs >= thresh

    buggy_preds <- preds[data$buggy]
    clean_preds <- preds[!data$buggy]

    tp <- sum(ifelse(buggy_preds == T, 1, 0))
    fp <- sum(ifelse(clean_preds == T, 1, 0))
    tpr <- append(tpr, tp / length(buggy_preds))
    fpr <- append(fpr, fp / length(clean_preds))
  }

  #plot(fpr, tpr, xlim=c(0,1), ylim=c(0,1))

  return(-areauc(fpr, tpr))
}

aucec <- function(fit, data, cutoff=1) {
  x <- "churn"
  y <- "bugcount"
  o <- "bugdens"

  churncut <- sum(data[,x]) * cutoff

  baseorder <- order(-data[,x])
  optorder <- order(-data[,o])

  myorder <- NULL
  if (class(fit)[1] == "lrm") {
    preds <- predict(fit, data)
    myorder <- order(-(exp(preds)/(1+exp(preds))))
  } else if(class(fit)[1] == "ols") {
    myorder <- order(-predict(fit, data))
  }

  # Cutoffs
  baseorder <- baseorder[cumsum(data[baseorder,"churn"]) <= churncut]
  optorder <- optorder[cumsum(data[optorder,"churn"]) <= churncut]
  myorder <- myorder[cumsum(data[myorder,"churn"]) <= churncut]

  optarea <- areauc(cumsum(data[optorder,x]), cumsum(data[optorder,y]))
  myarea <- areauc(cumsum(data[myorder,x]), cumsum(data[myorder,y]))
  basearea <- areauc(cumsum(data[baseorder,x]), cumsum(data[baseorder,y]))

  return((myarea-basearea)/(optarea-basearea))
}

aucec.optimism <- function(fit, data, B, cutoff=1) {
  rtnv <- c()

  for (i in 1:B) {
    # Derive bootstrap sample
    bootdata <- data[sample(1:nrow(data), replace=T),]

    # Fit model to bootstrap
    refit <- ols(fit$sformula, data=bootdata, x=T, y=T)

    # apply to bootstrap and orig data
    bootAUCEC <- aucec(refit, bootdata, cutoff)
    origAUCEC <- aucec(refit, data, cutoff)

    # compute difference
    rtnv <- append(rtnv, bootAUCEC - origAUCEC)
  }

  return(mean(rtnv))
}

aucec.dropone <- function(fit, train, test=NULL, testvars=NULL, cutoff=1) {
  # Split the formula into a list of explanatory variables
  formsplit <- strsplit(as.character(fit$sformula), " ~ ", fixed=T)
  outcome <- formsplit[[2]]
  vars <- strsplit(formsplit[[3]], " + ", fixed=T)[[1]]
  fitfunc <- get(class(fit)[1])

  if (is.null(test)) {
    test = train
  }

  # For each explanatory variable, refit the model without it
  if (is.null(testvars)) {
    for (i in 1:length(vars)) {
      myvars <- vars[!(1:length(vars) %in% i)]
      refit <- fitfunc(as.formula(paste(outcome, paste(myvars, collapse = " + "), sep = " ~ ")), data=train, x=T, y=T, tol=1e-12)

      fullmodelAUCEC <- aucec(fit, test, cutoff)
      deltaAUCEC <- (fullmodelAUCEC-aucec(refit, test, cutoff))/fullmodelAUCEC

      print(paste(vars[i], round(deltaAUCEC, digits=2), sep=": "))
    }
  } else {
    myvars <- c()
    for(var in vars) {
      cleanvar <- gsub("rcs(", "", gsub(")", "", gsub(",.*$", "", var), fixed=T), fixed=T)
      if (!(cleanvar %in% testvars)) {
        myvars <- append(var, myvars)
      }
    }

    deltaAUCEC = NA
    if (length(myvars) < length(vars)) { # variable under test is there
      refit <- fitfunc(as.formula(paste(outcome, paste(myvars, collapse = " + "), sep = " ~ ")), data=train, x=T, y=T, tol=1e-12)

      fullmodelAUCEC <- aucec(fit, test, cutoff)
      deltaAUCEC <- (fullmodelAUCEC-aucec(refit, test, cutoff))/fullmodelAUCEC
    }

    return(ifelse(is.na(deltaAUCEC), NA, round(deltaAUCEC, digits=2)))
  }
}
