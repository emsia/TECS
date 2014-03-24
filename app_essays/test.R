library(lsa)
library(tm)
library(cluster)

args <- commandArgs(trailingOnly = TRUE)
#args <- c("/home/nowhere/Desktop/CS199TECS/app_essays/essays/computers", "test.csv", "result.csv")

setwd(args[1])
testfilename = args[2]
automatedScores = args[3]
load('training_file.RData')
load('TrainingMatrix.RData')
load('training_matrix.RData')
testfile = read.csv(testfilename, header=F)
test.corpus <- Corpus(DataframeSource(data.frame(testfile[,1])));
test.corpus <- tm_map(test.corpus, removePunctuation);
test.corpus <- tm_map(test.corpus, tolower)
test.corpus <- tm_map(test.corpus, function(x) removeWords(x, stopwords("english")));
test.corpus <- tm_map(test.corpus, stemDocument)
testmatrix <- TermDocumentMatrix(test.corpus, control=list(dictionary=rownames(training_matrix)));
testmatrix = weightTfIdf(testmatrix, normalize=T)

concept.matrix <- NULL
for(i in 1:length(unique(training_file$V2))) {
  start <- as.numeric(row.names(head(training_file[training_file$V2==unique(training_file$V2)[i],],1)))
  end <- as.numeric(row.names(tail(training_file[training_file$V2==unique(training_file$V2)[i],],1)))
  km <- kmeans(t(TrainingMatrix)[start:end,],3)
  concept.matrix <- rbind(concept.matrix, km$centers)
  }
concept.matrix <- t(concept.matrix)

xstar <- solve(t(concept.matrix) %*% concept.matrix  ) %*% t(concept.matrix) %*% as.matrix(TrainingMatrix)
ystar <- solve(t(concept.matrix) %*% concept.matrix  ) %*% t(concept.matrix) %*% as.matrix(testmatrix)

#pred <- testfile[,2]
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
  testfile[a,2] <- training_file[index,2]
}
