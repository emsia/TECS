
import os
import hashlib
import random
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from app_schools.models import School, SchoolForm, EditForm
from django.shortcuts import render, get_object_or_404
from app_auth.models import UserProfile, SUadmin, School, Admin
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
	hasSchools = None
	power = False
	if suadmin:
		power = True
	link = 'app_schools/viewSchools.html'
	schools = School.objects.filter(suadmin=suadmin)
	administration = []
	for school in schools:
		try:
			admins = Admin.objects.filter(school=school)
			administration.append(admins)
		except:
			pass
	if power and (schools is None or not schools.exists()):
		hasSchools = 'You don\'t have Schools yet'
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
			name_info = forms['name']
			short_name_info = forms['short_name']
			address_info = forms['address']
			suadmin_info= SUadmin.objects.get(user=request.user)
			#rendered = render_to_string("users/emails/data.txt", {'data': data})
	
			school_info = School.objects.filter(name=name_info).filter(short_name=short_name_info).filter(address=address_info).filter(suadmin=suadmin_info)
			if school_info.exists():
				return suadmin_viewSchools(request, 'That School already exists.')

			form = form_school.save(commit=False)
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
def delete(request, school_id):
	school_info = get_object_or_404(School, pk=school_id)
	school_info.delete()
	return suadmin_viewSchools(request, 0, 'You successfully deleted a school.')

@login_required(redirect_field_name='', login_url='/')
def viewSchoolAdmins(request, school_id, message=None, success=True):
	school_info = get_object_or_404(School, pk=school_id)
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	formMails = MailForm2()
	hasAdmin = None
	power = True
	admins = Admin.objects.filter(school=school_info)
	if power and (admins is None or not admins.exists()):
		hasAdmin = 'This school doesn\'t have admins yet.'

	return render(request, 'app_schools/viewSchoolAdmins.html', {'mailSend':False, 'school':school_info, 'adminList':admins, 'avatar':avatar, 'succ': success,'success':message, 'formMails': formMails,  'active_nav':'SCHOOLS'})

@login_required(redirect_field_name='', login_url='/')
def removeAdmin(request):
	school_info = get_object_or_404(School, pk=request.POST['school_id'])
	admin = get_object_or_404(Admin, pk=request.POST['admin_id'])
	school_info.admin.remove(admin)
	return viewSchoolAdmins(request, request.POST['school_id'], 'You successfully removed an admin.')

@login_required(redirect_field_name='', login_url='/')
def addAdmin(request,  school_id, add_form=None, email_form=None):
	avatar = UserProfile.objects.get(user_id = request.user.id).avatar
	school_info = get_object_or_404(School, pk=school_id)
	adminAdd_form = adminAdd()
	admin = Admin.objects.filter(user=request.user)
	formMails = email_form or MailForm()
	return render(request, 'app_schools/add_admin.html', 
			{'adminAdd_form':adminAdd_form, 'formMails':formMails,'next_url': '/schools/', 'avatar':avatar, 'active_nav':'SCHOOLS'})


@login_required(redirect_field_name='', login_url='/')
def submitAdmins(request):
	if request.method == "POST":
		form_school = adminAdd(data=request.POST)
		mails = request.POST.getlist('email')
		usernames = request.POST.getlist('username')

		#print mails: check proper email addresses
		message = ''
		for email in mails:
			try:
				validate_email(email)
				pass
			except ValidationError:
				message = 'Please input valid emails'

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
				admin = Admin.objects.create(user=new_user)
				admin.save()
				count = count + 1

		return redirect('/schools/')

