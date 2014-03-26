# args[1] directory [2] testcsv [3] resultcsv [4] myLSAspace [5] trainingcsv
library(tm)
library(lsa)
library(MASS)

args <- commandArgs(trailingOnly = TRUE)
setwd(args[1])

#args <- c("./essays/computers", "test.csv", "result.csv")

featureVectors <- list()

#Mode <- function(x) {
#  ux <- unique(x)
#  ux[which.max(tabulate(match(x, ux)))]
#}

Mode <- function(x) {
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

whichpart <- function(x, n=3) {
  nx <- length(x)
  p <- nx-n+1
  xp <- sort(x, partial=p)[p:nx]
  c(which(x==xp[1])[1],  which(x==xp[2])[1],  which(x==xp[3])[1])
}

#setwd(args[1])
testFile = args[2]
automatedScores = args[3]
#training_file = args[5]
#load('myLSAspace.RData')
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
#test.corpus <- tm_map(test.corpus, stemDocument)

#convert to matrix
test_matrix <- TermDocumentMatrix(test.corpus, control=list(dictionary=rownames(training_matrix)));

#TFIDF -- bnag kaka NaN(not a numeric) dahil hindi nag eexist yung word. Dapat machange to "0" yung mga NaN
#TestMatrix = lw_logtf(test_matrix) * gw_idf(test_matrix)
TestMatrix = weightTfIdf(test_matrix, normalize=T)
n <- as.matrix(TestMatrix)

#fold in the test matrix to exisitng LSA Space
#tem_red = fold_in(n, myLSAspace)
#j <- as.matrix(tem_red)

train <- as.matrix(TrainingMatrix)
rm(TrainingMatrix)

if(ncol(train) <= 35){
  j <- ceiling(ncol(train)/5)
} else
  j <- 35 # 35 will be the minimum

cand <- mat.or.vec(j,2)

for(i in 1:j){
  cand[i,1] <- (kmeans(t(train), i+2))$tot.withinss
  cand[i,2] <- i + 2
}

if(j>1){
  result <- mat.or.vec(j-1,1)
} else
  result <- mat.or.vec(j,1)

if(nrow(cand) > 1){
  result[1:j-1] <- cand[1:j-1,1] - cand[2:j,1];
} else
  result[1] <- cand[1];

result[result<0] <- ""

k <- which.min(result)

centers_kmeans <- (kmeans(t(train), k, algorithm="Hartigan-Wong"))
centers_kmeans <- t(centers_kmeans$centers)

a <- 0.04
centers_kmeans[abs(centers_kmeans) <a] <- 0

inv <- ginv(t(centers_kmeans) %*% centers_kmeans)
X_train <-  inv %*% (t(centers_kmeans) %*% train)
Q_test <- inv %*% (t(centers_kmeans) %*% n);

pred <- td[,2]
cos <- mat.or.vec(ncol(Q_test),ncol(X_train))
    
for(a in 1:ncol(Q_test)){
  for(b in 1:ncol(X_train)){
    cos[a,b] <- cosine(Q_test[,a],X_train[,b])
  }
}

sco <- as.matrix(apply(cos[,1:ncol(X_train)], 1, whichpart))
a = training_file[sco,2]
h <- matrix(a,ncol = 3)
k <- as.matrix(apply(h[,3:1], 1, Mode))

td[,2] <- k
#knnn = ""

#knnnn=knn(t(train),t(j),cl=training_file[,2],k=3)
#indices = attr(knnnn, "nn.index")
#a = training_file[indices,2]
#h <- matrix(a,ncol = 3)
#k <- as.matrix(apply(h[,3:1], 1, Mode))
#plot(knnnn)

confusion <- table(factor(k, levels = unique(pred)),pred)

#rm(pred, cos)

EAA <- sum(diag(confusion))/ncol(Q_test)

write.table(td, file=automatedScores,row.names=FALSE, col.names=FALSE, sep=",")
write.table(confusion, file=paste0(EAA,"_EAA_ConfusionMatrix.csv"),sep=",")

#AAA <- sum(diag(confusion))
#AAA <- AAA + sum(diag(confusion[2:nrow(confusion),1:ncol(confusion)-1]))
#AAA <- AAA + sum(diag(confusion[1:nrow(confusion)-1,2:ncol(confusion)]))
#AAA <- AAA/ncol(Q_test)

#resultMatrix <- do.call(rbind, featureVectors)

#colnames(resultMatrix) <- c("EAA","AAA")
#write.csv(resultMatrix, file="resultMatrix_ci_knn.csv")
