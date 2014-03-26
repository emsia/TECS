library(lsa)
library(tm)
args <- commandArgs(trailingOnly = TRUE)

setwd(args[1])
#setwd("/home/nowhere/Desktop/CS199TECS/app_essays/essays/13 computer and its effects")
trainingfilename = args[2]
testfilename = args[3]
resultfilename = args[4]


# Read files
trainingfile = read.csv(trainingfilename, header=F)
testfile = read.csv(testfilename, header=F)

########## STEP 1: PREPROCESSING ##########


##### DATA CLEANING
#make bunch of words from training_file
training.corpus <- Corpus(DataframeSource(data.frame(trainingfile[,1])));
test.corpus <- Corpus(DataframeSource(data.frame(testfile[,1])));

#remove the punctuation marks
training.corpus <- tm_map(training.corpus, removePunctuation);
test.corpus <- tm_map(test.corpus, removePunctuation);

#make the corpus into lowercase
training.corpus <- tm_map(training.corpus, tolower)
test.corpus <- tm_map(test.corpus, tolower)

##### REMOVAL OF STOPWORDS
training.corpus <- tm_map(training.corpus, function(x) removeWords(x, stopwords("english")));
test.corpus <- tm_map(test.corpus, function(x) removeWords(x, stopwords("english")));

##### STEMMING
training.corpus <- tm_map(training.corpus, stemDocument)
test.corpus <- tm_map(test.corpus, stemDocument)

#convert training.corpus into term-document matrix
trainingmatrix <- TermDocumentMatrix(training.corpus);
testmatrix <- TermDocumentMatrix(test.corpus, control=list(dictionary=rownames(trainingmatrix)));

#weight by Term Frequency - Inverse Document Frequency
trainingmatrix = weightTfIdf(trainingmatrix, normalize=T)
#testmatrix = weightTfIdf(testmatrix, normalize=T)

#Sub-cluster the training document vectors for each score category using Fuzzy C-Means
#fannyx <- fanny(t(trainingmatrix), 6)
#fannyx
#summary(fannyx)
#plot(fannyx)

#Sub-cluster the training document vectors for each score category using K-Means
#concept.matrix <- NULL
#km <- kmeans(t(trainingmatrix), 5)
#concept.matrix <- t(km$centers)

concept.matrix <- NULL
for(i in 1:length(unique(trainingfile$V2))) {
  start <- as.numeric(row.names(head(trainingfile[trainingfile$V2==unique(trainingfile$V2)[i],],1)))
  end <- as.numeric(row.names(tail(trainingfile[trainingfile$V2==unique(trainingfile$V2)[i],],1)))
  km <- kmeans(t(trainingmatrix)[start:end,],1)
  #km <-skmeans(t(trainingmatrix)[start:end,],3,m=1)
  #for(j in 1:3) {
  #  rmeans = t(colMeans(km$prototype[,km$cluster==1], na.rm=TRUE))
  #  concept.matrix <- rbind(concept.matrix, rmeans)
  #}
  concept.matrix <- rbind(concept.matrix, km$centers)
  #concept.matrix <- rbind(concept.matrix, centers(km))
}
concept.matrix <- t(concept.matrix)

#Concept Decomposition and Folding In
xstar <- solve(t(concept.matrix) %*% concept.matrix  ) %*% t(concept.matrix) %*% as.matrix(trainingmatrix)
ystar <- solve(t(concept.matrix) %*% concept.matrix  ) %*% t(concept.matrix) %*% as.matrix(testmatrix)

pred <- testfile[,2]
for(a in 1:ncol(ystar)) {
  temp <- 0
  cos <- -9999
  index <- 0
  for(b in 1:ncol(xstar)){
    temp <- cosine(ystar[,a],xstar[,b])
    if (cos < temp){
      cos <- temp #highest cos value
      index <- b #most similar docu
    }
  }
  testfile[a,2] <- trainingfile[index,2]
}
write.table(testfile, file=resultfilename,row.names=FALSE, col.names=FALSE, sep=",")


confusion <- table(factor(testfile[,2], levels = unique(pred)),pred)
EAA <- sum(diag(confusion))/ncol(ystar)
AAA <- sum(diag(confusion))
AAA <- AAA + sum(diag(confusion[2:nrow(confusion),1:ncol(confusion)-1]))
AAA <- AAA + sum(diag(confusion[1:nrow(confusion)-1,2:ncol(confusion)]))
AAA <- AAA/ncol(ystar)

confusion
EAA
AAA

