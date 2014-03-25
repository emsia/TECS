
import os
import hashlib
import random
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from app_auth.models import School
from app_schools.models import SchoolForm, EditForm
from django.shortcuts import render, get_object_or_404
from app_auth.models import UserProfile, SUadmin, School, Admin
from app_classes.models import Class
from app_registration.models import RegistrationProfile
from django.db.models import Count
from django import forms
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from django.forms.widgets import Textarea
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from django.template import Context
from .forms import MultiEmailField, MailForm, MailForm2, adminAdd
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
def suadmin_viewSchools(request, err=None, success=None):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")

	User_Profile = User_Profile.get(user_id=request.user.id)
	suadmin = SUadmin.objects.filter(user=request.user)
	print suadmin
	hasSchools = None
	power = False
	if suadmin:
		power = True
	link = 'app_schools/viewSchools.html'
	schools = School.objects.filter(suadmin=suadmin)
	#schools = School.objects.all()
	administration = []
	for school in schools:
		try:
			admins = Admin.objects.filter(school=school)
			administration.append(admins)
		except:
			pass
	if power and (schools is None or not schools.exists()):
		hasSchools = 'You don\'t have schools yet.'
	avatar = User_Profile.avatar
	return render(request, link, {'avatar':avatar, 'schools':schools, 'hasSchools':hasSchools, 'power':power, 'active_nav':'SCHOOLS', 'administrations':administration})
		
@login_required(redirect_field_name='', login_url='/')
def suadmin_addNewSchool(request, add_form=None, email_form=None):
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	addSchool_form = add_form or SchoolForm()
	suadmin = SUadmin.objects.filter(user=request.user)
	name = School.objects.filter(suadmin=suadmin)
	return render(request, 'app_schools/suadmin_addNewSchool.html', 
			{'addSchoolForm' : addSchool_form, 'next_url': '/schools/', 'avatar':avatar, 'name':name, 'active_nav':'SCHOOLS'})

@login_required(redirect_field_name='', login_url='/')
def submit(request):
	if request.method == "POST":
		form_school = SchoolForm(data=request.POST)
		if form_school.is_valid():
			forms = form_school.cleaned_data
			name_info = forms['name'].title()
			short_name_info = forms['short_name'].title()
			address_info = forms['address'].title()
			suadmin_info= SUadmin.objects.get(user=request.user)
			#rendered = render_to_string("users/emails/data.txt", {'data': data})
	
			school_info = School.objects.filter(name=name_info).filter(short_name=short_name_info).filter(address=address_info).filter(suadmin=suadmin_info)
			if school_info.exists():
				return suadmin_viewSchools(request, 'That School already exists.')

			School.objects.create(name=name_info , short_name=short_name_info, address= address_info)
			#forms['name'] = name_info
			#forms['short_name'] = short_name_info
			#forms['address'] = address_info
			#form = form_school.save(commit=False)
			form = School.objects.get(name=name_info , short_name=short_name_info, address= address_info)
			#form.name = name_info
			#forms['short_name'] = short_name_info
			#forms['address'] = address_info
			#print(forms['name'])
			form.suadmin = suadmin_info
			form.date_created = timezone.now()
			form.is_active = True

			random_data = os.urandom(128)
			random_data = hashlib.md5(random_data).hexdigest()[:16]
			form.key = random_data
			form.save()

			success_url = request.POST.get("next_url", '/schools/')
			return redirect(success_url)
		else:
			return suadmin_addNewSchool(request, form_school)


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

	place = "base/base_suadmin.html"
	if not power:
		formEdit = EditForm(initial={'name':school_info.name, 'short_name':school_info.short_name, 'address':school_info.address})
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	return render(request, 'app_schools/suadmin_editSchool.html', {'avatar':avatar, 'next_url': '/schools/','school_info':school_info, 'place':place, 'formEdit':formEdit,  'active_nav':'SCHOOLS'})
			
@login_required(redirect_field_name='', login_url='/')
def delete(request):
	school_info = get_object_or_404(School, pk=request.POST['school_id'])	
	classes = Class.objects.filter(school=school_info)
	if (classes.exists()):
		return suadmin_viewSchools(request, 0, 'You cannot delete this school. Delete all of its classes first.')
	else:
		school_info.delete()
		return suadmin_viewSchools(request, 0, 'You successfully deleted a school.')

@login_required(redirect_field_name='', login_url='/')
def viewSchoolAdmins(request, school_id, message=None, error=None, success=True):
	school_info = get_object_or_404(School, pk=school_id)
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	formMails = MailForm2()
	admins = Admin.objects.filter(school=school_info)
	hasAdmin=True
	if (admins is None or not admins.exists()):
		hasAdmin=False
	return render(request, 'app_schools/viewSchoolAdmins.html', {'mailSend':False, 'school':school_info, 'adminList':admins, 'avatar':avatar, 'succ': success,'message':message, 'error':error, 'formMails': formMails, 'hasAdmin':hasAdmin, 'active_nav':'SCHOOLS'})


@login_required(redirect_field_name='', login_url='/')
def removeAdmin(request):
	admin = get_object_or_404(Admin, pk=request.POST['admin_id'])
	school_info = get_object_or_404(School, pk=request.POST['school_id'])
	admin.delete()
	return viewSchoolAdmins(request, request.POST['school_id'], 'You successfully removed an admin.')

@login_required(redirect_field_name='', login_url='/')
def addAdmin(request,  school_id, add_form=None, email_form=None):
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	school_info = get_object_or_404(School, pk=school_id)
	adminAdd_form = adminAdd()
	formMails = email_form or MailForm()
	return render(request, 'app_schools/add_admin.html', 
			{'school':school_info, 'adminAdd_form':adminAdd_form, 'formMails':formMails,'next_url': '/schools/', 'avatar':avatar, 'active_nav':'SCHOOLS'})


@login_required(redirect_field_name='', login_url='/')
def submitAdmins(request):
	message = None
	if request.method == "POST":
		form_school = adminAdd(data=request.POST)
		mails = request.POST.getlist('email')
		lasts = request.POST.getlist('last_name')
		firsts = request.POST.getlist('first_name')
		usernames = request.POST.getlist('username')

		for email in mails:
			try:
				validate_email(email)
				pass
			except ValidationError:
				message = 'Please input valid emails'
		if not message:
			print request.POST['school_id']
			school = get_object_or_404(School, pk=request.POST['school_id'])
			count = 0
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
					new_user.last_name = lasts[count].title()
					new_user.first_name = firsts[count].title()
					new_user.save()
					admin = Admin.objects.create(user=new_user)
					admin.school = school
					admin.save()
					count = count + 1

		return redirect('/schools/')
	return add_admin(request, form_school, message)


@login_required(redirect_field_name='', login_url='/')
def send_newPassword(request):
	email = request.POST['newMail']
	message = None
	school_id = request.POST['school_id']
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
		u = User.objects.get(pk=user_id)
		u.set_password(password_preset)
		u.email = email
		u.is_active = True
		u.save()

		template = get_template('app_schools/send_newPassword.html').render(
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
		mailSend.send()
		message = 'Changing complete'
		error = 0

	return viewSchoolAdmins(request, school_id, message, error, True)
