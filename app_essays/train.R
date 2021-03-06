library(tm);
library(lsa);
args <- commandArgs(trailingOnly = TRUE)
#args <- c("/home/nowhere/Desktop/CS199TECS/app_essays/essays/17 censorship in the libraries", "training.csv")
setwd(args[1])
trainingFile <- args[2];
    
training_file <- read.csv(trainingFile, header=F);
save(training_file, file='training_file.RData')

#make bunch of words from training_file.
training.corpus <- Corpus(DataframeSource(data.frame(training_file[,1])));
    
#remove the punctuation marks
training.corpus <- tm_map(training.corpus, removePunctuation);
    
#make the corpus into tolower
training.corpus <- tm_map(training.corpus, tolower);
    
#remove all the stopwords
training.corpus <- tm_map(training.corpus, function(x) removeWords(x, stopwords("english")));
    
#stemming
#training.corpus <- tm_map(training.corpus, stemDocument)
    
#gagawin lang nyang matrix yung termdocument matrix
training_matrix <- TermDocumentMatrix(training.corpus);
save(training_matrix, file='training_matrix.RData')
    
#tfidf weightTfIdf
TrainingMatrix = weightTfIdf(training_matrix, normalize=F)
save(TrainingMatrix, file='TrainingMatrix.RData')

