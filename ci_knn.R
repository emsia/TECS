#in R studio, click packages -> Install Packages: tm
#set the directory first
library(tm)
library(lsa)
library(MASS)

featureVectors <- list()
time <- list()

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

for(l in 1:8){
  for(m in 1:4){
    ptm <- proc.time()
    trainingFile = "";
    testFile = "";
    
    trainingFile = paste("corrected_training/training",l,sep='')
    trainingFile = paste(trainingFile,".csv",sep='')
    
    testFile = paste("corrected_test/test",l,sep='')
    testFile = paste(testFile,".csv",sep='')    
    
    autmatedScores = paste("AutomatedScores_ci_knn/training",l,sep='');
    
    if(m==1){  #stemming only
      type = "with stemming";
      autmatedScores = paste(autmatedScores,"_st.csv",sep='');
      tw = paste("t",l,sep='')
      tw = paste(tw,"st.csv",sep='')
    }
    if(m==2){ #stop words only
      type = "with stopwords";
      autmatedScores = paste(autmatedScores,"_sw.csv",sep='');
      tw = paste("t",l,sep='')
      tw = paste(tw,"sw.csv",sep='')
    }
    if (m==3){ #Both
      type = "with stemming and stopwords";
      autmatedScores = paste(autmatedScores,"_swst.csv",sep='');
      tw = paste("t",l,sep='')
      tw = paste(tw,"swst.csv",sep='')
    }
    if(m==4) { #none
      type = "none";
      autmatedScores = paste(autmatedScores,"_n.csv",sep='');
      tw = paste("t",l,sep='')
      tw = paste(tw,".csv",sep='')
    }
    
    #matrix1 = textmatrix("training.csv", minWordLength=1, stemming=TRUE, stopwords=stopwords_en, removeNumbers=TRUE)
    training_file <- read.csv(trainingFile, header=F);
    
    #make bunch of words from training_file.
    training.corpus <- Corpus(DataframeSource(data.frame(training_file[,1])));
    
    #remove the punctuation marks
    training.corpus <- tm_map(training.corpus, removePunctuation);
    
    #make the corpus into tolower
    training.corpus <- tm_map(training.corpus, tolower);
    
    #remove all the stopwords
    if(m==2 || m==3)
      training.corpus <- tm_map(training.corpus, function(x) removeWords(x, stopwords("english")));
    
    #stemming
    if(m==1 || m==3)
      training.corpus <- tm_map(training.corpus, stemDocument)
    
    #gagawin lang nyang matrix yung termdocument matrix
    training_matrix <- TermDocumentMatrix(training.corpus);
    
    #tfidf weightTfIdf
    #TrainingMatrix = lw_logtf(training_matrix) * gw_idf(training_matrix)
    TrainingMatrix = weightTfIdf(training_matrix, normalize=F)
    
    #LSA
    #myLSAspace = lsa(TrainingMatrix, dims=50)
    #me <- round(as.textmatrix(myLSAspace),2)
    #read a one test document, but we can put every test document in one csv file
    
    td <- read.csv(testFile, header=F)
    
    test.corpus <- Corpus(DataframeSource(data.frame(td[,1])));
    
    #remove the punctuation marks
    test.corpus <- tm_map(test.corpus, removePunctuation);
    
    #make the corpus into tolower
    test.corpus <- tm_map(test.corpus, tolower);
    
    #remove all the stopwords
    if(m==2 || m==3)
      test.corpus <- tm_map(test.corpus, function(x) removeWords(x, stopwords("english")));
    
    #stemming
    if(m==1 || m==3)
      test.corpus <- tm_map(test.corpus, stemDocument)
    
    test_matrix <- TermDocumentMatrix(test.corpus, control=list(dictionary=rownames(training_matrix)));
    
    #TFIDF -- bnag kaka NaN(not a numeric) dahil hindi nag eexist yung word. Dapat machange to "0" yung mga NaN
    #TestMatrix = lw_logtf(test_matrix) * gw_idf(test_matrix)
    TestMatrix = weightTfIdf(test_matrix, normalize=F)
    n <- as.matrix(TestMatrix)
    
    #fold in the test matrix to exisitng LSA Space
    #tem_red = fold_in(n, myLSAspace)
    #j <- as.matrix(tem_red)
    
    #myLSAspace = "";
    #n = "";
    rm(training_matrix, test_matrix, TestMatrix, test.corpus, training.corpus);
    
    train <- as.matrix(TrainingMatrix)
    rm(TrainingMatrix)
    
    save(n,td, training_file, file="mess.RData")
    save.image()
    
    rm(n,td,training_file)
    
    #candidate_kmeans <- kmeans(train, 12, algorithm="Hartigan-Wong");
    #j <- floor(ncol(train)/10)
    j <- 35 # 35 will be the minimum
    cand <- mat.or.vec(j,2)
    
    for(i in 1:j){
      cand[i,1] <- (kmeans(t(train), i+2))$tot.withinss
      cand[i,2] <- i + 2
    }
    save(cand, file="candMe.RData")
    load("mess.RData", .GlobalEnv)
    unlink("mess.RData")
    #for visual purpose
    #plot(cand[1:j,1])
    #lines(cand[1:j,1])
    
    result <- mat.or.vec(j-1,1)
    result[1:j-1] <- cand[1:j-1,1] - cand[2:j,1]
    result[result<0] <- ""
    rm(cand)
    #result <- result[which(result!="")]
    
    k <- which.min(result)
    rm(result)
    centers_kmeans <- (kmeans(t(train), k, nstart=25, algorithm="Hartigan-Wong"))
    centers_kmeans <- t(centers_kmeans$centers)
    #plot(train, col = centers_kmeans$cluster)
    
    ## reduced train
    a <- 0.04
    centers_kmeans[abs(centers_kmeans) <a] <- 0
    #r <- qr(centers_kmeans)
    #r <- qr.R(r)
    inv <- ginv(t(centers_kmeans) %*% centers_kmeans)
    X_train <-  inv %*% (t(centers_kmeans) %*% train)
    Q_test <- inv %*% (t(centers_kmeans) %*% n);
    
    rm(train, n, inv, centers_kmeans)
    
    pred <- td[,2]
    #for(a in 1:ncol(Q_test)){
    #  temp <- 0
    #  cos <- 0
    #  index <- 0
    #  for(b in 1:ncol(X_train)){
    #    temp <- cosine(Q_test[,a],X_train[,b])
    #    if (cos < temp){ 
    #      cos <- temp #highest cos value
    #      index <- b #most similar docu
    #    }
    #  }
    #  td[a,2] <- training_file[index,2]
    #}
    
    cos <- mat.or.vec(ncol(Q_test),ncol(X_train))
    
    for(a in 1:ncol(Q_test)){
      for(b in 1:ncol(X_train)){
        cos[a,b] <- cosine(Q_test[,a],X_train[,b])
      }
    }
    
    save(td, training_file, Q_test, file="mess.RData")
    save.image()
    rm(td, training_file, Q_test)
    
    sco <- as.matrix(apply(cos[,1:ncol(X_train)], 1, whichpart))      
    load("mess.RData", .GlobalEnv)
    unlink("mess.RData")
    
    a = training_file[sco,2]
    h <- matrix(a,ncol = 3)
    
    k <- as.matrix(apply(h[,3:1], 1, Mode))
    td[,2] <- k
    
    confusion <- table(factor(k, levels = unique(pred)),pred)
    
    rm(pred, cos)
    
    EAA <- sum(diag(confusion))/ncol(Q_test)
    
    write.table(td, file=autmatedScores,row.names=FALSE, col.names=FALSE, sep=",")
    write.table(confusion, file=paste("EAA_ConfusionMatrices_ci_knn",paste(EAA,tw,sep='_'),sep="/"),sep=",")
    
    AAA <- sum(diag(confusion))
    AAA <- AAA + sum(diag(confusion[2:nrow(confusion),1:ncol(confusion)-1]))
    AAA <- AAA + sum(diag(confusion[1:nrow(confusion)-1,2:ncol(confusion)]))
    AAA <- AAA/ncol(Q_test)
    
    file = "";
    name <- paste("feat_", m, sep="");
    
    features <- c(EAA, AAA)
    file <- paste("Data Set ", l, sep="");
    file <- paste(file, " - ", sep="");
    file <- paste(file, type, sep="");
    assign(name, file)
    
    featureVectors[[get(name)]] <- features
    mee <- proc.time() - ptm
    time[[paste("test ", get(name), sep="")]] <- c(mee)
    
    rm(myLSAspace, test.corpus, training.corpus, autmatedScores, training_file)
    rm(train, td, j, tw)
  }
}

timeMatrix <- do.call(rbind, time)

resultMatrix <- do.call(rbind, featureVectors)
colnames(resultMatrix) <- c("EAA","AAA")
write.csv(resultMatrix, file="resultMatrix_ci_knn_Unique.csv")

write.csv(timeMatrix, file="time_ci_knn_unique.csv")
