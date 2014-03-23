# args[1] directory [2] testcsv [3] resultcsv [4] myLSAspace [5] trainingcsv
library(tm);
library(lsa);
library(FNN);

args <- commandArgs(trailingOnly = TRUE)
args <- c("/home/nowhere/Desktop/CS199TECS/app_essays/essays/computers", "test.csv", "result.csv")

featureVectors <- list()

Mode <- function(x) {
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}


setwd(args[1])
testFile = args[2]
automatedScores = args[3]
#training_file = args[5]
load('myLSAspace.RData')
load('training_matrix.RData')
load('TrainingMatrix.RData')
load('training_file.RData')

#read a one test document, but we can put every test document in one csv file
td <- read.csv(testFile, header=F)

test.corpus <- Corpus(DataframeSource(data.frame(td[,1])));

#remove the punctuation marks
test.corpus <- tm_map(test.corpus, removePunctuation);

#make the corpus into tolower
test.corpus <- tm_map(test.corpus, tolower);

#remove all the stopwords
test.corpus <- tm_map(test.corpus, function(x) removeWords(x, stopwords("english")));

#stemming
test.corpus <- tm_map(test.corpus, stemDocument)

#convert to matrix
test_matrix <- TermDocumentMatrix(test.corpus, control=list(dictionary=rownames(training_matrix)));

#TFIDF -- bnag kaka NaN(not a numeric) dahil hindi nag eexist yung word. Dapat machange to "0" yung mga NaN
#TestMatrix = lw_logtf(test_matrix) * gw_idf(test_matrix)
TestMatrix = weightTfIdf(test_matrix, normalize=F)
n <- as.matrix(TestMatrix)

#fold in the test matrix to exisitng LSA Space
tem_red = fold_in(n, myLSAspace)
j <- as.matrix(tem_red)

train <- as.matrix(TrainingMatrix)
TrainingMatrix = "";

pred <- td[,2]
knnn = ""

knnnn=knn(t(train),t(j),cl=training_file[,2],k=3)
indices = attr(knnnn, "nn.index")
a = training_file[indices,2]
h <- matrix(a,ncol = 3)
k <- as.matrix(apply(h[,3:1], 1, Mode))
#plot(knnnn)

confusion <- table(factor(k, levels = unique(pred)),pred)
EAA <- sum(diag(confusion))/ncol(j)

write.table(td, file=automatedScores,row.names=FALSE, col.names=FALSE, sep=",")
write.table(confusion, file=paste("EAA_ConfusionMatrix.csv"))

AAA <- sum(diag(confusion))
AAA <- AAA + sum(diag(confusion[2:nrow(confusion),1:ncol(confusion)-1]))
AAA <- AAA + sum(diag(confusion[1:nrow(confusion)-1,2:ncol(confusion)]))
AAA <- AAA/ncol(j)

resultMatrix <- do.call(rbind, featureVectors)

colnames(resultMatrix) <- c("EAA","AAA")
write.csv(resultMatrix, file="resultMatrix_knn.csv")
