from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.formsets import formset_factory, BaseFormSet
from django.core.context_processors import csrf
from email.MIMEImage import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from app_auth.models import UserProfile, Student, Teacher
from app_essays.models import Essay, EssayResponse, GradingSystem, EssayForm, EssayComment, Grade, EssayResponseForm, EssayResponseGradeForm, EssayCommentForm
from app_classes.models import Class

#from rq import Queue
#from run_worker import conn

from app_essays import tasks

from datetime import datetime
from random import choice
import operator, urllib, re, csv, subprocess, os, pprint, collections
import nltk, json

@login_required(redirect_field_name='', login_url='/')
def new_essay(request):
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	errors = 0;
	teacher = get_object_or_404(Teacher, user_id = request.user.id)
	classlist = Class.objects.filter(teacher = teacher)
	has_class = Class.objects.filter(teacher = teacher).exists()

	if request.method == 'POST':
		form = EssayForm(request.POST, request)
		#form.fields['class_name'].queryset = Class.objects.filter(teacher = Teacher.objects.get(user_id = request.user.id))
		if form.is_valid():
			cd = form.cleaned_data
			data = form.save(commit=False)
			data.instructor = Teacher.objects.get(user_id = request.user.id)
			data.status = 1
			data.save()

			for essayclass in cd['class_name']:
				data.class_name.add(essayclass)
				emails = []
				for student in essayclass.student.all():
					response = EssayResponse(essay=data, essayclass=essayclass, student=student)
					response.save()
					emails.append(student.user.email)

				c = {
	                'user': request.user,
	                'class': essayclass,
	                'title': cd['title'],
	            }

				fp = open('./static/base/img/icons/notes.png', 'rb')
				msgImage = MIMEImage(fp.read())
				fp.close()
				msgImage.add_header('Content-ID', '<image1>')

				email = render_to_string('app_essays/new_essay_email.html', c)

				mailSend = EmailMessage('[TECS] New exam has started!', email, request.user.email, emails )
				mailSend.content_subtype = "html"
				mailSend.attach(msgImage)
				#mailSend.send()

			return list_essay(request, None, 'New exam has been added.')
		else :
			errors = 1
		
	else:
		form = EssayForm()
		form.fields['class_name'].queryset = classlist

	return render(request, 'app_essays/teacher_newExam.html', {'avatar':avatar, 'active_nav':'EXAMS', 'errors':errors, 'form': form, 'has_class':has_class, 'classlist':classlist})

@login_required(redirect_field_name='', login_url='/')	
def list_essay(request, errors=None, success=None):
	active_nav = "EXAMS"
	userProfile = UserProfile.objects.filter(user_id = request.user.id)
	if not userProfile.exists():
		return redirect("/profile")
	avatar = userProfile.get(user_id = request.user.id).avatar
	#IF USER IS A TEACHER
	if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
		no_on_going_essays = 0
		no_past_essays = 0
		no_on_queue_essays = 0

		on_queue_essays = Essay.objects.filter(instructor_id = Teacher.objects.get(user_id = request.user.id).id, status=1).filter(start_date__gt=timezone.now()).all()
		on_going_essays = Essay.objects.filter(instructor_id = Teacher.objects.get(user_id = request.user.id).id, status=1).filter(start_date__lte=timezone.now(), deadline__gte=timezone.now()).all()
		past_essays = Essay.objects.filter(Q(instructor_id = Teacher.objects.get(user_id = request.user.id).id, deadline__lt=timezone.now()) | Q(status=3)).order_by('deadline')
		
		#MANUAL WAY TO CHANGE STATUS OF AN ESSAY IF IT'S PAST THE DEADLINE
		EssayResponse.objects.filter(essay__status=1, essayclass__teacher=Teacher.objects.get(user_id = request.user.id)).filter(essay__deadline__lt=timezone.now()).update(status=2, response='')
		Essay.objects.filter(instructor_id = Teacher.objects.get(user_id = request.user.id).id).filter(deadline__lt=timezone.now()).update(status=2)
		
		'''
		essays.update(status=2)
		for essay in essays:
			for essayresponse in EssayResponse.objects.filter(essay=essay):
				essayresponse.status = 2
		'''
		if (len(on_queue_essays) == 0 ):
			no_on_queue_essays = 1	
		if (len(on_going_essays) == 0 ):
			no_on_going_essays = 1	
		if (len(past_essays) == 0):
			no_past_essays = 1
		return render(request, 'app_essays/teacher_viewExam.html',	{'avatar':avatar, 'active_nav':'EXAMS', 'no_on_queue_essays':no_on_queue_essays,'no_on_going_essays':no_on_going_essays, 'no_past_essays':no_past_essays, 'on_queue_essays':on_queue_essays,'on_going_essays':on_going_essays, 'past_essays':past_essays,'errors':errors, 'success':success})

	#IF USER IS A STUDENT
	elif len(Student.objects.filter(user_id = request.user.id)) > 0:
		#essays = Essay.objects.filter(instructor_id = Teacher.objects.get(user_id = request.user.id).id)
		no_on_going_essay_responses = 0
		no_past_essay_responses = 0

		#on_going_essay_responses = EssayResponse.objects.filter(~Q(status=2), student=Student.objects.get(user_id = request.user.id)).filter(essay__deadline__gte=timezone.now())
		on_going_essay_responses = EssayResponse.objects.filter(~Q(essay__status=-1), student=Student.objects.get(user_id = request.user.id)).filter(essay__start_date__lte=timezone.now(), essay__deadline__gte=timezone.now())
		past_essay_responses = EssayResponse.objects.filter(~Q(essay__status=-1), student=Student.objects.get(user_id = request.user.id)).filter(essay__deadline__lt=timezone.now())

		#MANUAL WAY TO CHANGE STATUS OF AN ESSAY IF IT'S PAST THE DEADLINE
		EssayResponse.objects.filter(essay__status__gt=-1, essay__status__lt=2, student=Student.objects.get(user_id = request.user.id)).filter(essay__deadline__lt=timezone.now()).update(status=2)

		if (len(on_going_essay_responses) == 0 ):
			no_on_going_essay_responses = 1	
		if (len(past_essay_responses) == 0):
			no_past_essay_responses = 1
		return render(request, 'app_essays/student_viewEssay.html', {'avatar':avatar, 'active_nav':'EXAMS','no_on_going_essay_responses':no_on_going_essay_responses, 'no_past_essay_responses':no_past_essay_responses, 'on_going_essay_responses':on_going_essay_responses, 'past_essay_responses':past_essay_responses, 'errors':errors, 'success':success})
		
@login_required(redirect_field_name='', login_url='/')
def exam_details(request, essay_id=None, class_id=None):
	active_nav = "EXAMS"
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	essay = get_object_or_404(Essay, pk=essay_id, instructor=Teacher.objects.get(user=request.user))

	if request.method == 'POST':
		essay_id_post = request.POST.get('essay-id')
		essay = Essay.objects.get(pk=essay_id_post)
		
		if 'CANCEL_EXAM' in request.POST:
			#print(essay)
			#essay.status = -1
			#essay.save()
			essay.delete()
			return redirect('essays:list')
		elif 'RELEASE_GRADES' in request.POST:
			essay.status = 3
			essay.save()
			return redirect('essays:list')
		elif 'AES' in request.POST:
			essay_responses = EssayResponse.objects.filter(essay_id=essay.pk, essayclass_id=class_id)
			possible_grade_values = Grade.objects.filter(grading_system=essay.grading_system)

			#CREATE A FOLDER FOR THE ESSAYTOPIC
			title = re.sub('[^A-Za-z\s]+', '', essay.title).lower()
			directory = './app_essays/essays/'+str(request.user.pk)+' '+title
			if not os.path.exists(directory):
				os.makedirs(directory)

			'''
			trainingcsv = 'training.csv'
			testcsv = 'test.csv'
			
			with open(directory+'/'+trainingcsv, 'a') as trainingfiles, open(directory+'/'+testcsv, 'wb') as testfiles:
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
			'''
			#q = Queue(connection=conn)
			#results = q.enqueue(the_making(request, directory, essay_response))
			## essay, class_id, directory
			results = tasks.the_making(request, essay, class_id, directory)

			'''
			with open(directory+'/'+trainingcsv, 'a') as trainingfiles, open(directory+'/'+testcsv, 'wb') as testfiles:
				csvwriter_training = csv.writer(trainingfiles, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				csvwriter_test = csv.writer(testfiles, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				forautograding = 0
				for essay_response in essay_responses:	
					e = re.sub('[^A-Za-z\s]+', '', essay_response.response)
					e = e.replace('', '')
					#print '---------------------------------------------------------'
					if e:
						if essay_response.grade is not None:
							csvwriter_training.writerow([e, essay_response.grade.pk])
						else:
							csvwriter_test.writerow([e, '', essay_response.pk])
							forautograding+=1
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
			retcode = subprocess.call(['/app/vendor/R/lib64/R/bin/Rscript', './app_essays/train.R', directory, trainingcsv])
			print retcode
			retcode = subprocess.call(['/app/vendor/R/lib64/R/bin/Rscript', './app_essays/test.R', directory, testcsv, resultcsv, directory+'/myLSAspace.RData', trainingcsv])
			print retcode
			print "****************** END TESTING ***********************"
			with open(directory+'/'+trainingcsv, 'a') as trainingfiles, open(directory+'/'+resultcsv, 'rb') as resultfile:
				resultreader = csv.reader(resultfile, delimiter=',', quotechar='|')
				csvwriter_training = csv.writer(trainingfiles, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				for row in resultreader:
					essaypk = row[2]
					essaygrade = row[1]
					essay_response = EssayResponse.objects.get(id=essaypk)
					essay_response.grade = Grade.objects.get(pk=essaygrade)
					essay_response.save()
					csvwriter_training.writerow([row[0], essaypk])
			for essay_response in essay_responses:
				essay_response.computer_grade = choice(possible_grade_values)
				essay_response.save()
			'''
				
			return redirect('essays:details', essay_id, class_id)
	else:
		essayclass = essay.class_name.get(pk=class_id)
		students = essayclass.student.all()
		essay_responses = sorted(EssayResponse.objects.filter(essay_id=essay.pk, essayclass_id=class_id), key=operator.attrgetter('student.user.last_name', 'student.user.first_name')) # I used this way of sorting because we cannot use order_by() for case insensitive sorting :(
		all_graded = not EssayResponse.objects.filter(essay_id=essay.pk, essayclass_id=class_id, grade=None).exists()

		if essay.deadline >= timezone.now():
			is_deadline = False
			return render(request, 'app_essays/teacher_viewExamInfo.html', {'avatar':avatar, 'active_nav':'EXAMS', 'essay':essay, 'essayclass':essayclass, 'essay_responses':essay_responses, 'is_deadline':is_deadline, 'all_graded':all_graded})
		else:
			is_deadline = True
			all_graded = EssayResponse.objects.filter(essay_id=essay.pk, grade=None).exists()
			return render(request, 'app_essays/teacher_viewExamInfo.html', {'avatar':avatar, 'active_nav':'EXAMS', 'essay':essay, 'essayclass':essayclass, 'essay_responses':essay_responses, 'all_graded':all_graded, 'is_deadline':is_deadline})

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

@login_required(redirect_field_name='', login_url='/')
def answer_essay(request, essay_response_id):
	active_nav = "EXAMS"
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	essay_response = get_object_or_404(EssayResponse, pk=essay_response_id, status__lt=2,student=get_object_or_404(Student, user=request.user))

	if essay_response.status == 0:
		essay_response.status = 1
		essay_response.time_started = datetime.now()
		essay_response.save()
		essay_response = EssayResponse.objects.get(pk=int(essay_response_id))


	if request.is_ajax():
		form = EssayResponseForm(request.POST, request)
		if form.is_valid():
			response_data = form.cleaned_data['response']
			essay_response.response = response_data
			essay_response.save()

			if request.POST['submission_type'] == 'DRAFT':
				data = {'message':'Saved!', 'has_errors':0}

			elif request.POST['submission_type'] == 'FINAL':
				essay_response.status = 2
				essay_response.time_finished = datetime.now()
				essay_response.save()
				data = {}
				
			else:
				print request.POST['submission_type']
				data = {'message':'', 'has_errors':1}
		else:
			data = {'message':'Something went wrong. Try again.', 'has_errors':1}
		
		return HttpResponse(json.dumps(data), content_type="application/json")

	elif request.method == 'POST':
		form = EssayResponseForm(request.POST, request)
		if form.is_valid():
			response_data = form.cleaned_data['response']
			essay_response.response = response_data
			essay_response.save()

			if 'draft' in request.POST:
				return redirect('essays:answer', essay_response_id=essay_response.pk)

			if 'final' in request.POST:
				essay_response.status = 2
				essay_response.time_finished = datetime.now()
				essay_response.save()
				return redirect('essays:submission', essay_response_id=essay_response.pk)
		else :
			errors = 1
		
	else:
		form = EssayResponseForm(initial={'response':essay_response.response})
		return render(request, 'app_essays/student_answerEssay.html', {'avatar':avatar, 'active_nav':'EXAMS', 'essay_response':essay_response, 'form':form})

@login_required(redirect_field_name='', login_url='/')
def essay_submission(request, class_id=None, essay_response_id=None):
	active_nav = "EXAMS"
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	#essay_response = get_object_or_404(EssayResponse, pk=essay_response_id, status=2)
	essay_response = EssayResponse.objects.get(pk=essay_response_id, status=2)
	numbered_response = ''

	if essay_response.response.isspace() or essay_response.response.strip() == '':
		has_submission = 0

	else:
		has_submission = 1
		tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')

		index = 1
		for paragraph in re.split('[\n\r]+', essay_response.response):
			sentences = tokenizer.tokenize(paragraph.strip())		
			numbered_response = numbered_response +"<p>"
			for i, sentence in enumerate(sentences):
				sentences[i] = '<sup>'+ str(index) +'</sup> ' + sentence
				index+=1
			numbered_response = numbered_response+''.join(sentences)+"</p>"

	#IF USER IS A TEACHER
	if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
		if not essay_response.essay.instructor == get_object_or_404(Teacher, user=request.user):
			raise Http404
		else:
			essayclass = essay_response.essay.class_name.get(pk=class_id)
			if essay_response.grade == None:
				#SPELLING AND GRAMMAR CHECKER
				#c = pycurl.Curl()
				#url_param = "http://localhost:8081/?language=en-US&text="+urllib.quote_plus(essay_response.response)
				#c.setopt(c.URL, str(url_param))
				#c.perform()

				class EvaluateEssayFormSet(BaseFormSet):
					def __init__(self, *args, **kwargs):
						super(EvaluateEssayFormSet, self).__init__(*args, **kwargs)
						for form in self.forms:
							form.empty_permitted = True

				EssayCommentFormSet = formset_factory(EssayCommentForm, formset=EvaluateEssayFormSet)
				if request.method == 'POST': # If the form has been submitted...
					er_form = EssayResponseGradeForm(request.POST) # A form bound to the POST data
					er_form.fields['grade'].queryset = Grade.objects.filter(grading_system = essay_response.essay.grading_system).order_by('value')
					c_formset = EssayCommentFormSet(request.POST, request.FILES)

					if er_form.is_valid() and c_formset.is_valid():
						cd = er_form.cleaned_data
						essay_response.grade = cd['grade']
						essay_response.general_feedback = cd['general_feedback']
						essay_response.save()

						#if c_formset.empty_permitted and not c_formset.has_changed():
						for form in c_formset.forms:
							if form.empty_permitted and form.has_changed():
								c = form.save(commit=False)
								c.essay = essay_response
								c.save()
						return redirect('essays:submission', essayclass.pk, essay_response.pk)
				else:
					er_form = EssayResponseGradeForm()
					er_form.fields['grade'].queryset = Grade.objects.filter(grading_system = essay_response.essay.grading_system).order_by('value')
					c_formset = EssayCommentFormSet()

				c = {'er_form': er_form,
					 'c_formset': c_formset,
					}
				c.update(csrf(request))
				return render(request, 'app_essays/teacher_viewEssaySubmission.html', {'avatar':avatar, 'active_nav':'EXAMS', 'essay_response':essay_response, 'has_submission':has_submission, 'er_form':er_form, 'c_formset':c_formset, 'numbered_response':numbered_response, 'essayclass':essayclass})
			
			else:
				
				comments = EssayComment.objects.filter(essay=essay_response)
				return render(request, 'app_essays/teacher_viewEssaySubmission_Graded.html', {'avatar':avatar, 'active_nav':'EXAMS', 'essay_response':essay_response, 'has_submission':has_submission, 'comments':comments, 'numbered_response':numbered_response, 'essayclass':essayclass})
	
	#IF USER IS A STUDENT
	elif len(Student.objects.filter(user_id = request.user.id)) > 0:
		if not essay_response.student == get_object_or_404(Student, user=request.user):
			raise Http404
		else:
			comments = None
			if essay_response.grade != None:
				comments = EssayComment.objects.filter(essay=essay_response)
			return render(request, 'app_essays/student_viewEssaySubmission.html', {'avatar':avatar, 'active_nav':'EXAMS', 'essay_response':essay_response, 'has_submission':has_submission, 'comments':comments, 'numbered_response':numbered_response})

def time_remaining_ajax(request, essay_response_id):
	essay_response = get_object_or_404(EssayResponse, pk=essay_response_id, status=2,student=get_object_or_404(Student, user=request.user))
	data = {'time_remaining':essay_response.time_remaining}
	return HttpResponse(json.dumps(data), content_type="application/json")

def graderList(request):

	active_nav = "EXAMS"
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	essay_response = get_object_or_404(EssayResponse, pk=3, status=2)
	numbered_response = ''

	if essay_response.response.isspace() or essay_response.response.strip() == '':
		has_submission = 0

	else:
		has_submission = 1
		tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')

		index = 1
		for paragraph in re.split('[\n\r]+', essay_response.response):
			sentences = tokenizer.tokenize(paragraph.strip())		
			numbered_response = numbered_response +"<p>"
			for i, sentence in enumerate(sentences):
				sentences[i] = '<sup>'+ str(index) +'</sup> ' + sentence
				index+=1
			numbered_response = numbered_response+''.join(sentences)+"</p>"

	#IF USER IS A TEACHER
	if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
		if not essay_response.essay.instructor == get_object_or_404(Teacher, user=request.user):
			raise Http404
		else:	
			if essay_response.grade == None:
				#SPELLING AND GRAMMAR CHECKER
				#c = pycurl.Curl()
				#url_param = "http://localhost:8081/?language=en-US&text="+urllib.quote_plus(essay_response.response)
				#c.setopt(c.URL, str(url_param))
				#c.perform()

				class EvaluateEssayFormSet(BaseFormSet):
					def __init__(self, *args, **kwargs):
						super(EvaluateEssayFormSet, self).__init__(*args, **kwargs)
						for form in self.forms:
							form.empty_permitted = True

				EssayCommentFormSet = formset_factory(EssayCommentForm, formset=EvaluateEssayFormSet)
				if request.method == 'POST': # If the form has been submitted...
					er_form = EssayResponseGradeForm(request.POST) # A form bound to the POST data
					er_form.fields['grade'].queryset = Grade.objects.filter(grading_system = essay_response.essay.grading_system).order_by('value')
					c_formset = EssayCommentFormSet(request.POST, request.FILES)

					if er_form.is_valid() and c_formset.is_valid():
						cd = er_form.cleaned_data
						essay_response.grade = cd['grade']
						essay_response.general_feedback = cd['general_feedback']
						essay_response.save()

						#if c_formset.empty_permitted and not c_formset.has_changed():
						for form in c_formset.forms:
							if form.empty_permitted and form.has_changed():
								c = form.save(commit=False)
								c.essay = essay_response
								c.save()
						return redirect('essays:list')
				else:
					er_form = EssayResponseGradeForm()
					er_form.fields['grade'].queryset = Grade.objects.filter(grading_system = essay_response.essay.grading_system).order_by('value')
					c_formset = EssayCommentFormSet()

				c = {'er_form': er_form,
					 'c_formset': c_formset,
					}
				c.update(csrf(request))
				return render(request, 'app_auth/graded.html', {'avatar':avatar, 'active_nav':'EXAMS', 'essay_response':essay_response, 'has_submission':has_submission, 'er_form':er_form, 'c_formset':c_formset, 'numbered_response':numbered_response})
			
			else:
				comments = EssayComment.objects.filter(essay=essay_response)
				return render(request, 'app_auth/graded.html', {'avatar':avatar, 'active_nav':'EXAMS', 'essay_response':essay_response, 'has_submission':has_submission, 'comments':comments, 'numbered_response':numbered_response})
	
