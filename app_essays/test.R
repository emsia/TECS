library(lsa)
library(tm)
library(MASS)

args <- commandArgs(trailingOnly = TRUE)
#args <- c("/home/nowhere/Desktop/CS199TECS/app_essays/essays/17 censorship in the libraries", "test.csv", "result.csv")

setwd(args[1])
testfilename = args[2]
automatedScores = args[3]
load('training_file.RData')
load('TrainingMatrix.RData')
load('training_matrix.RData')

Mode <- function(x) {
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

whichpart <- function(x, n=3) {
  nx <- length(x)
  p <- nx-n+1
  xp <- sort(x, partial=p, decreasing=TRUE)[1:3]
  c(which(x==xp[1])[1],  which(x==xp[2])[1],  which(x==xp[3])[1])
}

testfile = read.csv(testfilename, header=F)
test.corpus <- Corpus(DataframeSource(data.frame(testfile[,1])));
test.corpus <- tm_map(test.corpus, removePunctuation);
test.corpus <- tm_map(test.corpus, tolower)
test.corpus <- tm_map(test.corpus, function(x) removeWords(x, stopwords("english")));
#test.corpus <- tm_map(test.corpus, stemDocument)
testmatrix <- TermDocumentMatrix(test.corpus, control=list(dictionary=rownames(training_matrix)));
testmatrix = weightTfIdf(testmatrix, normalize=T)

n <- as.matrix(testmatrix)
train <- as.matrix(TrainingMatrix)

if(ncol(train) <= 35){
  j <- ceiling(ncol(train)/10)
} else
  j <- 35 
print(j)
cand <- mat.or.vec(j,2)

for(i in 1:j){
  set.seed(1234)
  cand[i,1] <- (kmeans(t(train), i))$tot.withinss
  #cand[i,1] <- (kmeans(t(train), i))$tot.withinss
  cand[i,2] <- i + 2
}

result <- mat.or.vec(j-1,1)
result[1:j-1] <- cand[1:j-1,1] - cand[2:j,1]
result[result<0] <- ""

k <- which.min(result)
set.seed(1234)
centers_kmeans <- (kmeans(t(train), k, nstart=j, algorithm="Hartigan-Wong"))
centers_kmeans <- t(centers_kmeans$centers)
#plot(train, col = centers_kmeans$cluster)

## reduced train
a <- 0.04
centers_kmeans[abs(centers_kmeans) <a] <- 0
inv <- ginv(t(centers_kmeans) %*% centers_kmeans)
X_train <-  inv %*% (t(centers_kmeans) %*% train)
Q_test <- inv %*% (t(centers_kmeans) %*% n);

cos <- mat.or.vec(ncol(Q_test),ncol(X_train))

for(a in 1:ncol(Q_test)){
  for(b in 1:ncol(X_train)){
    cos[a,b] <- cosine(Q_test[,a],X_train[,b])
  }
}

sco <- as.matrix(apply(cos[,1:ncol(X_train)], 1, whichpart))

a <- training_file[sco,2]
h <- matrix(a,ncol = 3)

k <- as.matrix(apply(h[,3:1], 1, Mode))
testfile[,2] <- k

write.table(testfile, file=automatedScores,row.names=FALSE, col.names=FALSE, sep=",")