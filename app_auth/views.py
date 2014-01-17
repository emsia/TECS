try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
   
from app_registration import signals
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth import (
	REDIRECT_FIELD_NAME, login, logout, authenticate
)
from  django.contrib.auth.views import logout_then_login
from django.contrib.auth.models import User, check_password
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.core.context_processors import csrf
from app_auth.models import UserProfile, passwordForm, Student, Teacher, School, SUadmin, Admin
from app_classes.models import Class
from app_essays.models import Essay, EssayResponse
from app_essays.models import GradingSystem, GradeSysForm, Grade
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import LoginForm, PasswordForm, ProfileForm, schoolForStudent, schoolForTeacher, GradeForm_Option1, GradeForm_Option2, NewSuperAdminForm
from app_classes.forms import MailForm

import numpy, random, string, datetime

class LoginView(FormView):
	form_class = LoginForm
	redirect_field_name = REDIRECT_FIELD_NAME
	template_name = 'app_auth/login.html'
	success_url = '/dashboard'
	
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated():
			return HttpResponseRedirect(self.get_success_url())
		else:
			return super(LoginView, self).dispatch(request, *args, **kwargs)
	
	def form_valid(self, form, request):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
			
		user = authenticate(username=username, password=password)
			
		if user is not None:
			if user.is_active:
				login(self.request, user)
				return HttpResponseRedirect(self.get_success_url())
			else:
				return self.form_invalid(form, request, 'Account not yet Validated.')		
		else:		
			return self.form_invalid(form, request, 'Invalid username and password Combination.')
	
	def form_invalid(self, form, request, err=None):
		return render_to_response( self.template_name , {
			'errors': err,
			'form' : form, 
		},  RequestContext(request))
	
	def get_success_url(self):
		if self.success_url:
			redirect_to = self.success_url
		else:
			redirect_to = self.request.REQUEST.get(self.redirect_field_name, '')

		netloc = urlparse(redirect_to)[1]
		
		if not redirect_to:
			redirect_to = settings.LOGIN_REDIRECT_URL
		elif netloc and netloc != self.request.get_host():
			redirect_to = settings.LOGIN_REDIRECT_URL
		return redirect_to
	  
	def post(self, request, *args, **kwargs):
		c = {}
		c.update(csrf(request))
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		
		if form.is_valid():
			return self.form_valid(form, request)
		else:				
			return self.form_invalid(form, request, 'Please input username and password.')

def user_logout(request):
    return logout_then_login(request,login_url='/')

@login_required(redirect_field_name='', login_url='/')
def profile_view(request):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)

	if not User_Profile.exists():
		if len(Admin.objects.filter(user_id = request.user.id)) > 0 or len(SUadmin.objects.filter(user_id = request.user.id)):
			return redirect('auth:edit_SU_Admin')
		return redirect('auth:edit_profile')
	
	avatar = UserProfile.objects.get(user_id=request.user.id).avatar
	role = UserProfile.objects.get(user_id = request.user.id).role
	profile = UserProfile.objects.get(user=request.user)
	if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
		role = 'Teacher'
	elif len(Student.objects.filter(user_id = request.user.id)) > 0:
		role = 'Student'
	if len(Admin.objects.filter(user_id = request.user.id)) > 0:
		role = 'Admin'
	elif len(SUadmin.objects.filter(user_id = request.user.id)) > 0:
		role = 'SUadmin'
	return render(request, 'app_auth/profile_view.html', {'avatar': avatar, 'role':role, 'profile':profile, 'role':role})


@login_required(redirect_field_name='', login_url='/')
def edit_SU_Admin(request, success=None):
	user_info = UserProfile.objects.filter(user_id = request.user.id)
	power = False
	if request.method == "POST":
		formProfile = ProfileForm(request.POST, request.FILES)

		if formProfile.is_valid():
			temp = formProfile.cleaned_data
			if user_info.exists():
				#userProfile update
				userProfile_info = user_info.get(user_id=request.user.id)
				userProfile_info.avatar = userProfile_info.avatar

				if userProfile_info.avatar is None or not temp['avatar']:
					userProfile_info.avatar = 'images/avatars/user.png'
				elif temp['avatar'] is not None:
					userProfile_info.avatar = temp['avatar']	
				
				userProfile_info.street = temp['street'].title()
				userProfile_info.municipality = temp['municipality'].title()
				userProfile_info.province = temp['province'].title()
				userProfile_info.phone_number = temp['phone_number']
				userProfile_info.save()

			else:
				if temp['avatar'] is None:
					temp['avatar'] = 'images/avatars/user.png'
				UserProfile.objects.create(avatar=temp['avatar'], user_id=request.user.id, street=temp['street'], municipality=temp['municipality'], province=temp['province'], phone_number=temp['phone_number'])
			
			#user update
			USER_info = User.objects.get(id=request.user.id)
			USER_info.last_name = temp['last_name'].title()
			USER_info.first_name = temp['first_name'].title()
			USER_info.email = temp['email']
			USER_info.username = temp['username']
			USER_info.save()
			return redirect("auth:profile")

	if user_info.exists():
		user_info = user_info.get(user_id=request.user.id)
		role = UserProfile.objects.get(user_id = request.user.id).role
		avatar = user_info.avatar
		if not power:
			formProfile = ProfileForm(initial={
				'last_name':request.user.last_name, 'first_name':request.user.first_name, 'email':request.user.email, 'avatar':user_info.avatar,
				'username': request.user.username, 'street':user_info.street, 'municipality':user_info.municipality,
				'province': user_info.province, 'phone_number': user_info.phone_number
			})
	else:
		role = None
		avatar = 'images/avatars/user.png'

		formProfile = ProfileForm(initial={'last_name':request.user.last_name, 'role':role, 'first_name':request.user.first_name, 'email':request.user.email,
			'username': request.user.username,})

	return render(request, 'app_auth/adminSUA_edit.html', {'avatar': avatar, 'role':role, 'active_nav':'PROFILE', 'success':success, 'formProfile':formProfile})


@login_required(redirect_field_name='', login_url='/')
def profile_edit(request, success=None):
	user_info = UserProfile.objects.filter(user_id = request.user.id)
	if len(Admin.objects.filter(user_id = request.user.id)) > 0 or len(SUadmin.objects.filter(user_id = request.user.id)):
		return redirect('auth:edit_SU_Admin')
	power = False
	if request.method == "POST":
		formProfile = ProfileForm(request.POST, request.FILES)
		schoolForm = schoolForStudent(request.POST)
		if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
			schoolForm = schoolForTeacher(request.POST)
		power = True
		
		if schoolForm.is_valid():
			if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
				temp = schoolForm.cleaned_data['school']
				teacher = Teacher.objects.filter(user=request.user)
				if not teacher.exists():
					teacher = Teacher.objects.create(user=request.user)
					teacher.save()
				else:
					teacher = teacher.get(user=request.user)
					teacher.school.clear()
				for school in temp:
					print(school)
					teacher.school.add(school)
			else:
				student = Student.objects.filter(user=request.user)
				school = School.objects.get(id=request.POST['school'])
				if not student.exists():
					student = Student.objects.create(user=request.user, school=school)
				else:
					student = Student.objects.get(user=request.user)
					student.school = school
					student.save()

		if formProfile.is_valid():
			temp = formProfile.cleaned_data
			if user_info.exists():
				#userProfile update
				userProfile_info = user_info.get(user_id=request.user.id)
				userProfile_info.avatar = userProfile_info.avatar

				if userProfile_info.avatar is None or not temp['avatar']:
					userProfile_info.avatar = 'images/avatars/user.png'
				elif temp['avatar'] is not None:
					userProfile_info.avatar = temp['avatar']	
				
				userProfile_info.street = temp['street'].title()
				userProfile_info.municipality = temp['municipality'].title()
				userProfile_info.province = temp['province'].title()
				userProfile_info.phone_number = temp['phone_number']
				userProfile_info.save()

			else:
				if temp['avatar'] is None:
					temp['avatar'] = 'images/avatars/user.png'
				UserProfile.objects.create(avatar=temp['avatar'], user_id=request.user.id, street=temp['street'], municipality=temp['municipality'], province=temp['province'], phone_number=temp['phone_number'])
			
			#user update
			USER_info = User.objects.get(id=request.user.id)
			USER_info.last_name = temp['last_name'].title()
			USER_info.first_name = temp['first_name'].title()
			USER_info.email = temp['email']
			USER_info.username = temp['username']
			USER_info.save()
			return redirect("auth:profile")

	if user_info.exists():
		schoolForm = schoolForStudent()
		user_info = user_info.get(user_id=request.user.id)
		role = UserProfile.objects.get(user_id = request.user.id).role

		if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
			schoolForm = schoolForTeacher(initial={'school':Teacher.objects.get(user=request.user).school.values_list('id',flat=True)})
		else:
			schoolForm = schoolForStudent(initial={'school':Student.objects.get(user=request.user).school})
		avatar = user_info.avatar
		if not power:
			try:
				schoolForm = schoolForStudent(initial={'school':Student.objects.get(user=request.user).school})
			except:
				pass
			if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
				schoolForm = schoolForTeacher(initial={'school':Teacher.objects.get(user=request.user).school.values_list('id',flat=True)})
			formProfile = ProfileForm(initial={
				'last_name':request.user.last_name, 'first_name':request.user.first_name, 'email':request.user.email, 'avatar':user_info.avatar,
				'username': request.user.username, 'street':user_info.street, 'municipality':user_info.municipality,
				'province': user_info.province, 'phone_number': user_info.phone_number
			})
	else:
		role = None
		schoolForm = schoolForStudent()
		if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
			schoolForm = schoolForTeacher(initial={'school':Teacher.objects.get(user=request.user).school.values_list('id',flat=True)})
		avatar = 'images/avatars/user.png'

		formProfile = ProfileForm(initial={'last_name':request.user.last_name, 'role':role, 'first_name':request.user.first_name, 'email':request.user.email,
			'username': request.user.username,})

	return render(request, 'app_auth/profile_edit.html', {'avatar': avatar, 'role':role, 'role':role, 'active_nav':'PROFILE', 'success':success, 'formProfile':formProfile, 'schoolForm':schoolForm})

@login_required(redirect_field_name='', login_url='/')
def password_edit(request, success=None):
	user_info = UserProfile.objects.filter(user_id = request.user.id)

	if not user_info.exists():
		return redirect("/profile")

	role = UserProfile.objects.get(user_id = request.user.id).role
	user_info = user_info.get(user_id = request.user.id)
	avatar = user_info.avatar
	err = None
	power = False
	if request.user.is_staff:
		power = True
	if request.method == "POST":
		form_class = PasswordForm(data=request.POST)
		if form_class.is_valid():
			forms = form_class.cleaned_data
			password = forms['password']
			newPassword = forms['ConfPassword']
			oldPassword = forms['OldPassword']
			u = User.objects.get(id=request.user.id)

			if u.check_password(oldPassword) and password == newPassword:
				u.set_password(newPassword)
				u.save()
				success = 'You have changed your password.'
			else:
				err = 'Passwords did not matched.'
	else:
		form_class = PasswordForm()

	return render(request, 'app_auth/changePassword.html', {'avatar': avatar, 'role':role, 'active_nav':'ACCOUNT', 'power':power,'user_info':user_info, 'form':form_class, 'error': err, 'success':success})

@login_required(redirect_field_name='', login_url='/')
def grading_system(request):
	avatar = UserProfile.objects.get(user_id=request.user.id).avatar
	role = UserProfile.objects.get(user_id = request.user.id).role

	gradingsys = GradingSystem.objects.filter(created_by=request.user, is_active=1)
	gradingsys_admin = GradingSystem.objects.filter(created_by=1, is_active=1)

	return render(request, 'app_auth/grading_systems.html', {'avatar': avatar, 'role':role, 'active_nav':'GRADESYS', 'gradingsys':gradingsys, 'gradingsys_admin':gradingsys_admin})

@login_required(redirect_field_name='', login_url='/')
def grading_system_view(request, gradeSys_id):
	gradesys = get_object_or_404(GradingSystem, Q(created_by__pk=1) | Q(created_by=request.user), pk=gradeSys_id, is_active=1)
	grades = Grade.objects.filter(grading_system=gradesys).order_by('value')
	by_admin = 1 if gradesys.created_by.pk == 1 else 0
	return render(request, 'app_auth/grading_systems_view.html', {'gradesys': gradesys, 'grades': grades, 'by_admin':by_admin})

@login_required(redirect_field_name='', login_url='/')
def grading_system_new(request):
	avatar = UserProfile.objects.get(user_id=request.user.id).avatar
	role = UserProfile.objects.get(user_id = request.user.id).role
	
	if request.method == 'POST':
		formSys = GradeSysForm(request.POST, request)
		if 'option1' in request.POST:
			formGrade1 = GradeForm_Option1(request.POST, request)
			formGrade2 = GradeForm_Option2()
			print formGrade1.data['grades']

			if formSys.is_valid() and formGrade1.is_valid():
				cd_sys = formSys.save(commit=False)
				cd_sys.created_by = request.user
				cd_sys.is_active = 1
				cd_sys.save()

				cd_grades = formGrade1.cleaned_data
				for idx, grade in enumerate(cd_grades['grades'].split(',')):
					Grade.objects.create(grading_system=cd_sys, name=grade, value=idx)

				return redirect('auth:gradesys')


		elif 'option2' in request.POST:
			formGrade1 = GradeForm_Option1()
			formGrade2 = GradeForm_Option2(request.POST, request)

			if formSys.is_valid() and formGrade2.is_valid():
				cd_sys = formSys.save(commit=False)
				cd_sys.created_by = request.user
				cd_sys.is_active = 1
				cd_sys.save()

				cd_grades = formGrade2.cleaned_data

				if cd_grades['start'] < cd_grades['end']:
					for idx, grade in enumerate(numpy.arange(cd_grades['start'], cd_grades['end']-1, abs(cd_grades['step']))):
						Grade.objects.create(grading_system=cd_sys, name=grade, value=idx)
				else:
					for idx, grade in enumerate(numpy.arange(cd_grades['start'], cd_grades['end']+1, -abs(cd_grades['step']))):
						Grade.objects.create(grading_system=cd_sys, name=grade, value=idx)
				
				return redirect('auth:gradesys')
	else:
		formSys = GradeSysForm()
		formGrade1 = GradeForm_Option1()
		formGrade2 = GradeForm_Option2()

	return render(request, 'app_auth/grading_systems_new.html', {'avatar': avatar, 'role':role, 'active_nav':'GRADESYS', 'formSys':formSys, 'formGrade1':formGrade1, 'formGrade2':formGrade2})


@login_required(redirect_field_name='', login_url='/')
def grading_system_delete(request):
	if request.method == 'POST':
		GradeSys = get_object_or_404(GradingSystem, pk=request.POST['gradesysid'], created_by=request.user)
		GradeSys.delete()
	return redirect('auth:gradesys')

def login_on_activation(sender, user, request, **kwargs):
    user.backend='django.contrib.auth.backends.ModelBackend' 
    login(request,user)
signals.user_activated.connect(login_on_activation)

def dashboard(request, email_form=None):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)

	if not User_Profile.exists():
		if len(Admin.objects.filter(user_id = request.user.id)) > 0 or len(SUadmin.objects.filter(user_id = request.user.id)):
			return redirect('auth:edit_SU_Admin')
		return redirect('auth:edit_profile')
	else:
		role = User_Profile.get(user_id=request.user.id).role

	avatar = User_Profile.get(user_id=request.user.id).avatar

	if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
		class_count = Class.objects.filter(teacher=Teacher.objects.get(user=request.user), is_active=1).count()
		exam_count = Essay.objects.filter(instructor = Teacher.objects.get(user = request.user), status=1).filter(start_date__lte=timezone.now(), deadline__gte=timezone.now()).count()
		needs_grading_count =   EssayResponse.objects.filter(essay=Essay.objects.filter(instructor_id = Teacher.objects.get(user_id = request.user.id).id).filter(deadline__lt=timezone.now()), grade=None).count()
		return render(request, 'app_auth/teacher_dashboard.html', {'avatar': avatar, 'role':role, 'class_count':class_count, 'exam_count':exam_count, 'needs_grading_count':needs_grading_count})
	elif len(Student.objects.filter(user_id = request.user.id)) > 0:
		class_count = Class.objects.filter(student=Student.objects.get(user=request.user), is_active=1).count()
		exam_count = EssayResponse.objects.filter(~Q(essay__status=0), student=Student.objects.get(user_id = request.user.id)).filter(essay__start_date__lte=timezone.now(), essay__deadline__gte=timezone.now()).count()
		in_progress_count = EssayResponse.objects.filter(~Q(essay__status=1), student=Student.objects.get(user_id = request.user.id)).filter(essay__start_date__lte=timezone.now(), essay__deadline__gte=timezone.now()).count()
		return render(request, 'app_auth/student_dashboard.html', {'avatar': avatar, 'role':role, 'class_count':class_count, 'exam_count':exam_count, 'in_progress_count':in_progress_count})

	elif len(Admin.objects.filter(user_id = request.user.id)) > 0:
		teacher_lists = Teacher.objects.filter(school=Admin.objects.get(user=request.user).school)
		classList = []
		for teacher_list in teacher_lists:
			try:
				classes = Class.objects.get(teacher=teacher_list)
				classList.append(classes)
			except:
				pass
		return render(request, 'app_auth/admin_dashboard.html', {'avatar': avatar, 'role':role, 'teacher_list':teacher_lists, 'classList':classList})

	elif len(SUadmin.objects.filter(user_id = request.user.id)) > 0:
		school_list = School.objects.filter().count()
		formMails = email_form or MailForm()
		return render(request, 'app_auth/suadmin_dashboard.html', {'avatar': avatar, 'role':role ,'formMails':formMails, 'school_list':school_list})
	 
@login_required(redirect_field_name='', login_url='/')
def help(request):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")
	avatar = User_Profile.get(user_id=request.user.id).avatar
	if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
		return render(request, 'app_auth/teacher_help.html', {'avatar':avatar, 'active_nav':'DASHBOARD'})
	elif len(Student.objects.filter(user_id = request.user.id)) > 0:
		return render(request, 'app_auth/student_help.html', {'avatar':avatar, 'active_nav':'DASHBOARD'})

def graderList(request):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")
	avatar = User_Profile.get(user_id=request.user.id).avatar
	if len(Teacher.objects.filter(user_id = request.user.id)) > 0:
		return render(request, 'app_auth/teacher_help.html', {'avatar':avatar, 'active_nav':'DASHBOARD'})
	elif len(Student.objects.filter(user_id = request.user.id)) > 0:
		return render(request, 'app_auth/graded.html', {'avatar':avatar, 'active_nav':'DASHBOARD'})

@login_required
def suadmin_viewsuperadmins(request, err=None, success=None):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")

	User_Profile = User_Profile.get(user_id=request.user.id)
	avatar = User_Profile.avatar
	superadmins = SUadmin.objects.filter(status__gte=0)


	return render(request, 'app_auth/suadmin_viewsuperadmins.html', {'avatar':avatar, 'superadmins':superadmins, 'active_nav':'SUPERADMIN'})

def suadmin_addsuperadmin(request, err=None, success=None):
	User_Profile = UserProfile.objects.filter(user_id = request.user.id)
	if not User_Profile.exists():
		return redirect("/profile")

	User_Profile = User_Profile.get(user_id=request.user.id)
	avatar = User_Profile.avatar
	
	if request.method == 'POST':
		form = NewSuperAdminForm(request.POST)
		if form.is_valid():
			while True:
				ac = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32))
				if not SUadmin.objects.filter(activation_code=ac).exists():
					break
			activation_code_expiry = datetime.datetime.now() + datetime.timedelta(days=7)

			user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], 'password')
			user.last_name = form.cleaned_data['last_name']
			user.first_name = form.cleaned_data['first_name']
			user.save()
			SUadmin.objects.create(user=user, registered_by=request.user, activation_code=ac, activation_code_expiry=activation_code_expiry)

			return redirect('auth:viewsuperadmins')
	else:
		form = NewSuperAdminForm
	
	return render(request, 'app_auth/suadmin_addsuperadmins.html', {'avatar':avatar, 'form':form, 'active_nav':'SUPERADMIN'})
