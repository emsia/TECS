
import os
import hashlib
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from app_schools.models import School, SchoolForm, EditForm
from django.shortcuts import render, get_object_or_404
from app_auth.models import UserProfile, SUadmin, School, Admin
from django.db.models import Count
from django import forms
from django.forms.widgets import Textarea
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from django.template import Context
from .forms import MailForm, MailForm2
from email.MIMEImage import MIMEImage

@login_required(redirect_field_name='', login_url='/')
def dashboard(request):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")
	avatar = User_Profile.get(user_id=request.user.id).avatar
	User_Profile = User_Profile.get(user_id=request.user.id)
	suadmin = SUadmin.objects.filter(user=request.user)
	avatar = User_Profile.avatar
	#return render(request, link, {'avatar':avatar, 'active_nav':'CLASSES', 'formEnroll':formEnroll, 'sections':sections, 'error': err, 'success':success, 'hasClasses':hasClasses, 'power':power})
	return render(request, link, {'avatar':avatar,'error': err, 'success':success, 'active_nav':'DASHBOARD'})

@login_required(redirect_field_name='', login_url='/')
def suadmin_viewSchools(request):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")

	User_Profile = User_Profile.get(user_id=request.user.id)
	suadmin = SUadmin.objects.filter(user=request.user)
	hasSchools = None
	power = True
	link = 'app_schools/viewSchools.html'
	schools = School.objects.filter(suadmin=suadmin)
	if power and (schools is None or not schools.exists()):
		hasSchools = 'You don\'t have Schools yet'
	avatar = User_Profile.avatar
	return render(request, link, {'avatar':avatar, 'schools':schools, 'hasSchools':hasSchools, 'power':power, 'active_nav':'SCHOOLS'})
		
@login_required(redirect_field_name='', login_url='/')
def suadmin_addNewSchool(request, add_form=None, email_form=None):
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	addSchool_form = add_form or SchoolForm()
	suadmin = SUadmin.objects.filter(user=request.user)
	name = School.objects.filter()
	formMails = email_form or MailForm()
	return render(request, 'app_schools/suadmin_addNewSchool.html', 
			{'addSchoolForm' : addSchool_form, 'formMails':formMails,'next_url': '/schools', 'avatar':avatar, 'name':name, 'active_nav':'SCHOOLS'})

@login_required(redirect_field_name='', login_url='/')
def submit(request):
	if request.method == "POST":
		form_school = SchoolForm(data=request.POST)
		formMails = MailForm(data=request.POST)
		success_url = request.POST.get("next_url", "/schools")

		if form_school.is_valid() and formMails.is_valid():
			forms = form_school.cleaned_data
			name_info = forms['name']
			short_name_info = forms['short_name']
			address_info = forms['address']

			emails = formMails.cleaned_data
			mail = []
			for email in emails.values():
				mail = email

			#rendered = render_to_string("users/emails/data.txt", {'data': data})
			try:
				suadmin_info = SUadmin.objects.get(user=request.user)
			except SUadmin.DoesNotExist:
				return school_suadmin(request, 'You don\'t have permission to add Schools.')

			school_info = School.objects.filter(name=name_info).filter(short_name=short_name_info).filter(address=address_info).filter(suadmin=suadmin_info)
			if school_info.exists():
				return school_suadmin(request, 'That School already exists.')

			form = form_school.save(commit=False)
			form.suadmin = suadmin_info
			form.date_created = timezone.now()
			form.is_active = True

			random_data = os.urandom(128)
			random_data = hashlib.md5(random_data).hexdigest()[:16]
			form.key = random_data
			form.save()

			template = get_template('app_schools/perl.html').render(
				Context({
					'sender': request.user,
					'adminList': form,
				})
			)
			if mail:
				fp = open('./static/base/img/icons/Mail@2x.png', 'rb')
				msgImage = MIMEImage(fp.read())
				fp.close()

				msgImage.add_header('Content-ID', '<image1>')

				mailSend = EmailMessage('[TECS] Invitation to join School', template, 'fsvaeg@gmail.com', mail )
				mailSend.content_subtype = "html"  # Main content is now text/html
				mailSend.attach(msgImage)
				mailSend.send()
			#send_mail('Subject', 'You are invited to class '+ yearType_info + '-' + section_info + ' ' + subject_info + '. The key class is: ' + random_data, 'fsvaeg@gmail.com', mail)
			
			return redirect(success_url)
		else:
			return suadmin_addNewSchool(request, form_school, formMails)


@login_required(redirect_field_name='', login_url='/')
def edit(request, school_id):
	school_info = get_object_or_404(School, pk=school_id)
	power = False
	if request.method == "POST":
		formEdit = EditForm(data=request.POST)
		power = True
		if formEdit.is_valid():
			temp = formEdit.cleaned_data
			school_info.name = temp['name']
			school_info.short_name = temp['short_name']
			school_info.address = temp['address']
			school_info.save()
			return viewSchoolAdmins(request, school_id, 'Changes to school details were saved.')

	if not power:
		formEdit = EditForm(initial={'name':school_info.name, 'short_name':school_info.short_name, 'section':school_info.address})
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	return render(request, 'app_schools/suadmin_editSchool.html', {'avatar':avatar, 'next_url': '/schools','school_info':school_info, 'formEdit':formEdit,  'active_nav':'SCHOOLS'})
			
@login_required(redirect_field_name='', login_url='/')
def delete(request):
	school_info = get_object_or_404(School, pk=request.POST['school_id'])
	school_info.delete()
	return school_suadmin(request, 0, 'You successfully deleted a school.')

@login_required(redirect_field_name='', login_url='/')
def viewSchoolAdmins(request, school_id, message=None, success=True):
	school_info = get_object_or_404(School, pk=school_id)
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	formMails = MailForm2()
	hasAdmin = None
	power = True
	admins = Admin.objects.filter(school=school_info)
	if power and (admins is None or not admins.exists()):
		hasAdmin = 'This school doesn\'t have admins yet'

	return render(request, 'app_schools/viewSchoolAdmins.html', {'mailSend':False, 'school':school_info, 'adminList':admins, 'avatar':avatar, 'succ': success,'success':message, 'formMails': formMails,  'active_nav':'SCHOOLS'})

@login_required(redirect_field_name='', login_url='/')
def removeAdmin(request):
	school_info = get_object_or_404(School, pk=request.POST['school_id'])
	admin = get_object_or_404(Admin, pk=request.POST['admin_id'])
	school_info.admin.remove(admin)
	return viewSchoolAdmins(request, request.POST['school_id'], 'You successfully removed an admin.')

@login_required(redirect_field_name='', login_url='/')
def inviteAdmin(request):
	school_id = request.POST['sid']
	school_info = get_object_or_404(School, pk=school_id)
	sender = request.user
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	message = 'Invalid Email address(es)'
	success = False
	mail = None
	count = 0

	if request.method == "POST":
		formMails = MailForm2(data=request.POST)
		sendNow = request.POST.get('sendNow')

		template = get_template('app_classes/perl.html').render(
			Context({
				'sender': sender,
				'adminList': school_info,
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

				mailSend = EmailMessage('[TECS] Invitation to join School', template, 'fsvaeg@gmail.com', mail )
				mailSend.content_subtype = "html"  # Main content is now text/html
				mailSend.attach(msgImage)
				mailSend.send()
				success = True
				message = 'Invitations were sent successfully.'
				return viewSchoolAdmins(request, school_id, message, success)
		else:
			return viewSchoolAdmins(request, school_id, message, success)
	else:
		formMails = MailForm2()

	#return viewClassList(request, class_id, message, success)
	return render(request, 'app_schools/viewSchoolAdmins.html', {'mails':mail, 'count':count, 'formMails':formMails,'sender':sender,'avatar':avatar, 'adminList':school_info, 'mailSend':True, 'active_nav':'SCHOOLS'})