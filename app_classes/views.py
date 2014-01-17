
import os
import hashlib
import random
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from app_classes.models import Class, ClassForm, EditForm, EnrollForm
from app_auth.models import Admin
from app_registration.models import RegistrationProfile
from django.shortcuts import render, get_object_or_404
from app_auth.models import UserProfile, Teacher, School, Student
from django.db.models import Count
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from django.forms.widgets import Textarea
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from django.template import Context
from .forms import MailForm, MailForm2, teacherAdd
from email.MIMEImage import MIMEImage

@login_required(redirect_field_name='', login_url='/')
def dashboard(request):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")
	avatar = User_Profile.get(user_id=request.user.id).avatar
	
	return render(request, 'app_classes/dashboard2.html', {'avatar':avatar, 'active_nav':'DASHBOARD'})
		
@login_required(redirect_field_name='', login_url='/')
def class_teacher(request, err=None, success=None, formStud=None):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")

	User_Profile = User_Profile.get(user_id=request.user.id)
	teacher = Teacher.objects.filter(user=request.user)
	hasClasses = None
	power = True
	formEnroll = formStud or EnrollForm()
	link = 'app_classes/class_teacher.html'
	if teacher.exists():
		sections = Class.objects.filter(teacher=teacher)
	else:
		student = Student.objects.filter(user=request.user)
		if student.exists():
			link = 'app_classes/viewClasses.html'
			sections = Class.objects.filter(student=student)
		else:
			sections = None
			power = False
			hasClasses = 'You have no permission to add Classes.'
	if power and (sections is None or not sections.exists()):
		hasClasses = 'You don\'t have Classes yet'
	avatar = User_Profile.avatar
	return render(request, link, {'avatar':avatar, 'active_nav':'CLASSES', 'formEnroll':formEnroll, 'sections':sections, 'error': err, 'success':success, 'hasClasses':hasClasses, 'power':power})

@login_required(redirect_field_name='', login_url='/')
def teacher_addNewClass(request, add_form=None, email_form=None):
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	addClass_form = add_form or ClassForm()
	teacher = Teacher.objects.filter(user=request.user)
	name = Class.objects.filter(teacher=teacher)
	formMails = email_form or MailForm()
	return render(request, 'app_classes/teacher_addNewClass.html', 
			{'addClassForm' : addClass_form, 'formMails':formMails,'next_url': '/classes', 'avatar':avatar, 'active_nav':'CLASSES', 'name':name})

@login_required(redirect_field_name='', login_url='/')
def add_teacher(request, form_class=None, error=None):
	message = ''
	try:
		check_priviledge = Admin.objects.get(user=request.user)
	except:
		message = "You don't have priviledge to add new teachers."
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	teacherAdd_form = form_class or teacherAdd()
	teacher = Teacher.objects.filter(user=request.user)
	name = Class.objects.filter(teacher=teacher)
	return render(request, 'app_classes/add_teacher.html', 
			{'teacherAdd_form':teacherAdd_form, 'next_url': '/classes', 'avatar':avatar, 'active_nav':'ADD_TEACHER', 'name':name, 'message':message, 'error':error})

@login_required(redirect_field_name='', login_url='/')
def submitTeachers(request):
	message = ''
	if request.method == "POST":
		form_class = teacherAdd(data=request.POST)
		mails = request.POST.getlist('email')
		usernames = request.POST.getlist('username')

		#print mails: check proper email addresses
		for email in mails:
			try:
				validate_email(email)
				pass
			except ValidationError:
				message = 'Please input valid emails'

		if not message:
			count = 0
			school = Admin.objects.get(user=request.user).school
			for usernaming in usernames:
				existing = User.objects.filter(username__iexact=usernaming)
				if not existing.exists():
					salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
					usernaming = usernaming.encode('utf-8')
					password_preset = hashlib.md5(salt+usernaming).hexdigest()[:12]
					print password_preset
					if Site._meta.installed:
						site = Site.objects.get_current()
					else:
						site = RequestSite(request)
					print password_preset
					new_user = RegistrationProfile.objects.create_inactive_user(usernaming, mails[count], password_preset, site)
					teacher = Teacher.objects.create(user=new_user)
					teacher.save()
					teacher.school.add(school)
					count = count + 1
			return redirect('auth:dashboard')
	return add_teacher(request, form_class, message)

@login_required(redirect_field_name='', login_url='/')
def viewTeachers(request, teacher_id, message=None, error=None):
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	teacher_details = get_object_or_404(Teacher, pk=teacher_id)
	class_info = Class.objects.filter(teacher=teacher_details)
	return render(request, 'app_classes/teacher_list.html', {'avatar':avatar, 'error':error, 'active_nav':'DASHBOARD', 'teacher_details':teacher_details, 'class_info': class_info, 'message':message})

@login_required(redirect_field_name='', login_url='/')
def submit(request):
	if request.method == "POST":
		form_class = ClassForm(data=request.POST)
		formMails = MailForm(data=request.POST)
		success_url = request.POST.get("next_url", "/")

		if form_class.is_valid() and formMails.is_valid():
			forms = form_class.cleaned_data
			school_info = forms['school']
			subject_info = forms['subject']
			yearType_info = forms['year_level']
			section_info = forms['section']
			academicYear_info = forms['academic_year']

			emails = formMails.cleaned_data
			mail = []
			for email in emails.values():
				mail = email

			#rendered = render_to_string("users/emails/data.txt", {'data': data})
			try:
				teacher = Teacher.objects.get(user=request.user)
			except Teacher.DoesNotExist:
				return class_teacher(request, 'You don\'t have permission to add Classes.')

			class_info = Class.objects.filter(school=school_info).filter(section=section_info).filter(subject=subject_info).filter(teacher=teacher).filter(year_level=yearType_info).filter(academic_year=academicYear_info)
			if class_info.exists():
				return class_teacher(request, 'That Class already exists.')

			form = form_class.save(commit=False)
			form.teacher = teacher
			form.date_created = timezone.now()
			form.is_active = True

			random_data = os.urandom(128)
			random_data = hashlib.md5(random_data).hexdigest()[:16]
			form.key = random_data
			form.save()

			template = get_template('app_classes/perl.html').render(
				Context({
					'sender': request.user,
					'studentList': form,
				})
			)
			if mail:
				fp = open('./static/base/img/icons/Mail@2x.png', 'rb')
				msgImage = MIMEImage(fp.read())
				fp.close()

				msgImage.add_header('Content-ID', '<image1>')

				mailSend = EmailMessage('[TECS] Invitation to join Class', template, 'fsvaeg@gmail.com', [mail] )
				mailSend.content_subtype = "html"  # Main content is now text/html
				mailSend.attach(msgImage)
				mailSend.send()
			#send_mail('Subject', 'You are invited to class '+ yearType_info + '-' + section_info + ' ' + subject_info + '. The key class is: ' + random_data, 'fsvaeg@gmail.com', mail)
			
			return redirect(success_url)
		else:
			return teacher_addNewClass(request, form_class, formMails)

@login_required(redirect_field_name='', login_url='/')
def disableTeacher(request, teacher_id, place=None):
	teacher_info = get_object_or_404(Teacher, pk=teacher_id)
	try:
		user_info = get_object_or_404(User, pk=teacher_info.user.id)
		user_info.is_active = not user_info.is_active
		user_info.save()
	except:
		pass

	if place == "1":
		return redirect('classes:viewTeachers', teacher_id=teacher_id)
	else:
		return redirect('auth:dashboard')

@login_required(redirect_field_name='', login_url='/')
def edit(request, class_id, place=None):
	class_info = get_object_or_404(Class, pk=class_id)
	power = False

	if place == "1":
		active_nav = 'CLASSES'
		place = 'base/base.html'
	else:
		active_nav = 'DASHBOARD'
		place = 'base/base_admin.html'

	if request.method == "POST":
		formEdit = EditForm(data=request.POST)
		power = True
		if formEdit.is_valid():
			temp = formEdit.cleaned_data
			class_info.school = temp['school']
			class_info.year_level = temp['year_level']
			class_info.section = temp['section']
			class_info.subject = temp['subject']
			class_info.academic_year = temp['academic_year']
			class_info.save()
			try:
				check_ifAdmin = Admin.objects.get(user=request.user)
				template = get_template('app_classes/notification.html').render(
					Context({
						'sender': check_ifAdmin,
						'school': temp['school'],
						'year_level' : temp['year_level'],
						'section' : temp['section'],
						'subject' : temp['subject'],
						'academic_year' : temp['academic_year']
					})
				)

				fp = open('./static/base/img/icons/Watches@2x.png', 'rb')
				msgImage = MIMEImage(fp.read())
				fp.close()

				msgImage.add_header('Content-ID', '<image1>')

				mailSend = EmailMessage('[TECS] Class Information Changed', template, 'fsvaeg@gmail.com', [class_info.teacher.user.mail] )
				mailSend.content_subtype = "html"  # Main content is now text/html
				mailSend.attach(msgImage)
				#mailSend.send()
			except:
				pass
			return viewClassList(request, class_id, '' ,'Changes to class details were saved.')

	if not power:
		formEdit = EditForm(initial={'school':class_info.school, 'year_level':class_info.year_level, 'section':class_info.section, 'academic_year':class_info.academic_year, 'subject':class_info.subject})
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	return render(request, 'app_classes/teacher_editClass.html', {'avatar':avatar, 'place':place, 'active_nav':active_nav, 'class_info':class_info, 'formEdit':formEdit})
			
@login_required(redirect_field_name='', login_url='/')
def delete(request):
	class_info = get_object_or_404(Class, pk=request.POST['class_id'])
	class_info.delete()
	return class_teacher(request, 0, 'You successfully deleted a class.')

@login_required(redirect_field_name='', login_url='/')
def viewClassList(request, class_id, place=None, message=None, success=True):
	class_info = get_object_or_404(Class, pk=class_id)
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	formMails = MailForm2()
	if place == "1":
		active_nav = 'CLASSES'
		place = 'base/base.html'
	else:
		active_nav = 'DASHBOARD'
		place = 'base/base_admin.html'
	return render(request, 'app_classes/viewClassList.html', {'mailSend':False, 'studentList':class_info, 'active_nav':active_nav, 'avatar':avatar, 'succ': success,'success':message, 'formMails': formMails, 'place': place})

@login_required(redirect_field_name='', login_url='/')
def enroll(request):
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	err = None
	if request.method == "POST":
		formEnroll = EnrollForm(data=request.POST)
		if formEnroll.is_valid():
			temp = formEnroll.cleaned_data
			key = temp['key']
			school = School.objects.filter(name=temp['school'])
			class_info = Class.objects.filter(school=school).filter(key=key)
			if class_info.exists():
				student = Student.objects.get(user=request.user)
				class_info = class_info.get(key=key)
				class_info.student.add(student)
				return class_teacher(request, 0, 'You are added to the class.')
			err = 'Invalid Key Combination.'
		else:
			err = 'There is unfilled form field.'
	else:
		formEnroll = EnrollForm()
	return class_teacher(request, err, 0, formEnroll)

@login_required(redirect_field_name='', login_url='/')
def removeStudent(request):
	place = request.POST['place']
	countless = "0"
	if place == 'base/base.html':
		countless = "1"

	class_info = get_object_or_404(Class, pk=request.POST['class_id'])
	student = get_object_or_404(Student, pk=request.POST['student_id'])
	class_info.student.remove(student)
	return viewClassList(request, request.POST['class_id'], countless, 'You successfully removed a student.')

@login_required(redirect_field_name='', login_url='/')
def inviteStudent(request):
	class_id = request.POST['cid']
	place = request.POST['place']
	class_info = get_object_or_404(Class, pk=class_id)
	sender = request.user
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	message = 'Invalid Email address(es)'
	success = False
	mail = None
	count = 0
	countless = "0"

	if place == 'base/base.html':
		active_nav = 'CLASSES'
		countless = "1"
	else:
		active_nav = 'DASHBOARD'

	if request.method == "POST":
		formMails = MailForm2(data=request.POST)
		sendNow = request.POST.get('sendNow')

		template = get_template('app_classes/perl.html').render(
			Context({
				'sender': sender,
				'studentList': class_info,
			})
		)
		if formMails.is_valid():
			emails = formMails.cleaned_data
			mail = []
			for email in emails.values():
				mail = email

			count = len(mail)
			if sendNow == 'sendNow':
				fp = open('./static/base/img/icons/Mail@2x.png', 'rb')
				msgImage = MIMEImage(fp.read())
				fp.close()

				msgImage.add_header('Content-ID', '<image1>')

				mailSend = EmailMessage('[TECS] Invitation to join Class', template, 'fsvaeg@gmail.com', [mail] )
				mailSend.content_subtype = "html"  # Main content is now text/html
				mailSend.attach(msgImage)
				#mailSend.send()
				success = True
				message = 'Invitations were sent successfully.'
				return viewClassList(request, class_id, countless, message, success)
		else:
			return viewClassList(request, class_id, countless, message, success)
	else:
		formMails = MailForm2()
	
	#return viewClassList(request, class_id, message, success)
	return render(request, 'app_classes/viewClassList.html', {'mails':mail, 'place':place, 'active_nav':active_nav, 'count':count, 'formMails':formMails,'sender':sender,'avatar':avatar, 'studentList':class_info, 'mailSend':True})

@login_required(redirect_field_name='', login_url='/')
def send_newPassword(request):
	email = request.POST['newMail']
	teacher_id = request.POST['teacher_id']
	message = ''
	error = 1

	try:
		validate_email(email)
	except ValidationError:
		message = 'Please input valid email'

	if not message:
		user_id = request.POST['user_account']
		usernaming = request.POST['username']

		salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
		usernaming = usernaming.encode('utf-8')
		password_preset = hashlib.md5(salt+usernaming).hexdigest()[:12]
		print password_preset
		u = User.objects.get(id=user_id)
		u.set_password(password_preset)
		u.email = email
		u.is_active = True
		u.save()

		template = get_template('app_classes/send_newPassword.html').render(
			Context({
				'sender': request.user,
				'pass': password_preset,
				'usernaming' : usernaming,
			})
		)

		fp = open('./static/base/img/icons/notes.png', 'rb')
		msgImage = MIMEImage(fp.read())
		fp.close()

		msgImage.add_header('Content-ID', '<image1>')

		mailSend = EmailMessage('[TECS] Password Change by Admin', template, 'fsvaeg@gmail.com', [email] )
		mailSend.content_subtype = "html"  # Main content is now text/html
		mailSend.attach(msgImage)
		#mailSend.send()
		message = 'Changing complete'
		error = 0

	return viewTeachers(request, teacher_id, message, error)