#from __future__ import absolute_import
import operator, urllib, re, csv, subprocess, os, pprint, collections
#from celery import shared_task, current_app, Celery
#from AEG.celery import app
#from djcelery import celery
from app_essays.models import Grade, EssayResponse
#from django.views.decorators.cache import cache_page
#from celery.contrib.methods import task_method, task
#from celery.decorators import task
#app = Celery('AEG')
#from celery import task

#@cache_page(60 * 15)
#@task
def the_making(essay, class_id, directory,title):
	print(directory)
	trainingcsv = 'training.csv'
	testcsv = 'test.csv'

	essay_responses = EssayResponse.objects.filter(essay_id=essay.pk, essayclass_id=class_id)
	possible_grade_values = Grade.objects.filter(grading_system=essay.grading_system)

	trainingfiles = open(directory+'/'+trainingcsv, 'a')
	testfiles = open(directory+'/'+testcsv, 'wb')

	csvwriter_training = csv.writer(trainingfiles, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	csvwriter_test = csv.writer(testfiles, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	forautograding = 0

	for essay_response in essay_responses:
		e = re.sub('[^A-Za-z\s]+', '', essay_response.response)
		e = e.replace('\r\n', '')
		#print '---------------------------------------------------------'
		if e:
			if essay_response.grade is not None:
				csvwriter_training.writerow([e, essay_response.grade.pk])
			else:
				csvwriter_test.writerow([e, '', essay_response.pk])
				forautograding+=1
	
	trainingfiles.close()
	testfiles.close()

	################### correcting misspelled words in training ##############################
	files = directory+'/'+trainingcsv
	file1 = open(files, 'rb')
	reader = csv.reader(file1)
	new_rows_list = []

	for row in reader:
		new_row = ' '.join(correct(t) for t in words(row[0])), row[1]
		new_rows_list.append(new_row)

	file1.close()
	file2 = open(directory+'/'+'training_corrected.csv', 'wb')

	writer = csv.writer(file2)
	writer.writerows(new_rows_list)
	file2.close()

	os.remove(directory+'/'+trainingcsv)
	os.rename(directory+'/'+'training_corrected.csv',directory+'/'+trainingcsv)

	##################### correcting misspelled words in test ###########################
	files = directory+'/'+testcsv
	file1 = open(files, 'rb')
	reader = csv.reader(file1)
	new_rows_list = []

	for row in reader:
		new_row = ' '.join(correct(t) for t in words(row[0])), row[1], row[2]
		new_rows_list.append(new_row)

	file1.close()
	file2 = open(directory+'/'+'test_corrected.csv', 'wb')

	writer = csv.writer(file2)
	writer.writerows(new_rows_list)
	file2.close()

	os.remove(directory+'/'+testcsv)
	os.rename(directory+'/'+'test_corrected.csv',directory+'/'+testcsv)

	#CALL R SCRIPT. PLEASE CHANGE THE LOCATION OF Rscript EXECUTABLE
	resultcsv = 'result.csv'
	retcode = subprocess.call(['/Library/Frameworks/R.framework/Versions/3.0/Resources/bin/Rscript', './app_essays/train.R', directory, trainingcsv])
	print retcode
	retcode = subprocess.call(['/Library/Frameworks/R.framework/Versions/3.0/Resources/bin/Rscript', './app_essays/test.R', directory, testcsv, resultcsv, directory+'/myLSAspace.RData', trainingcsv])
	print retcode
	print "****************** END TESTING ***********************"
	trainingfiles = open(directory+'/'+trainingcsv, 'a')
	resultfile = open(directory+'/'+resultcsv, 'rb')
	resultreader = csv.reader(resultfile, delimiter=',', quotechar='|')
	csvwriter_training = csv.writer(trainingfiles, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

	for row in resultreader:
		essaypk = row[2]
		essaygrade = row[1]
		essay_response = EssayResponse.objects.get(id=essaypk)
		essay_response.computer_grade = Grade.objects.get(pk=essaygrade)
		essay_response.save()
		csvwriter_training.writerow([row[0], essaypk])
	return True

def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

NWORDS = train(words(file('./app_essays/dictionary.txt').read()))

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    return max(candidates, key=NWORDS.get)
