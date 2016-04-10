require(rms)
require(plyr)

metrics = c("fix", "ns", "nd", "nf", "entrophy", "la", "ld", "lt", "ndev", "age", "nuc", "exp", "rexp", "sexp")
penaltySetting <- 2
num_iter <- 100
rq1 = "commit_words"
rq2 = "bayesian_score"
none = ""
depVar <- "contains_bug"
eventThresh <- 20
myd <- NA
alpha <- 7.396e-5


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

createPDF <- function(data, rq) {
  alpha <<- 0.05 / length(unique(data$name))

  pdf(paste('data/new/curves', rq, ".pdf", sep=""))

  ddply(data, "name", function(subdata) {
    le_lin_fit(subdata, metrics, rq)
  })

  dev.off()
}

make_pred_graph <- function(mydata, fit_obj, plot_var) {
  dd <<- datadist(mydata)
  options(datadist="dd")
  ret <- plot(Predict(fit_obj, bayesian_score, fun=function(x) { return(exp(x)/(1+exp(x))) }), xlab="Commit Content", ylab=" Defect Probability",asp="4:5", adj.subtitle=F)
}

le_lin_fit <- function(mydata, metrics, myvar){

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

  met <- append(metrics, myvar)
  if (subsetOkForFit(mydata)) {
    cleanMetrics <- getCleanMetrics(met,mydata)
    form <- paste(depVar, paste(cleanMetrics, collapse=" +"), sep = " ~ ")
    tryCatch({
      dd <<- datadist(mydata)
      options(datadist="dd")
      fit <- lrm(as.formula(form), data=mydata, x=T, y=T, penalty=penaltySetting)
      anv <- anova(fit, fit="Chisq")
      pval <- anv[44]
      if (pval < alpha){
        p = make_pred_graph(mydata,fit,myvar)
        # cat(paste(mydata$name[1]),file="rq2_sigs.txt",sep="\n",append=TRUE)
        print(p)
      }
      ret <- c(pval) 
      }, error = function(e) {
        print(paste("FIT FAILED: SKIPPING", mydata$name[1], sep=" "))
        ret <- c("NA")
      })
   } 
}
