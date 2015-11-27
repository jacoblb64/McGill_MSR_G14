## generating boxplots from a CSV file

args <- commandArgs(trailingOnly = TRUE)

# print(paste("now generating plots for"), args[1])

file_basename = sub("^([^.]*).*", "\\1", args[1]) 

pdf(paste(file_basename, "pdf", sep = "."), height = 6, width = 6, paper = 'special')


results = read.csv(args[1])
results["commit_length"] <- NA
results$commit_length <- nchar(as.character(results$commit_message))

fixes = subset(results, classification == "Corrective")
bugs = subset(results, contains_bug == TRUE)
no_bugs = subset(results, contains_bug = FALSE)

## four box plots
boxplot(results$commit_length, main="Commit length of all commits", ylab="commit length")
boxplot(fixes$commit_length, main="Commit length of corrective commits", ylab="commit length")
boxplot(bugs$commit_length, main="Commit length of bug containing commits", ylab="commit length")
boxplot(no_bugs$commit_length, main="Commit length of bug-less commits", ylab="commit length")

joined = merge( bugs$commit_length, no_bugs$commit_length)
names(joined) <- c("Bug Introducing", "Bug Free")
boxplot(joined, main = "Commit length of Bug Introducing and Bug Free Commits", ylab = "Length of commit")

dev.off()