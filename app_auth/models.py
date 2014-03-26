from django.db import models
from django.forms import ModelForm, PasswordInput
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	avatar = models.ImageField(upload_to='images/avatars/', default='images/avatars/user.png', blank=True)
	street = models.TextField(blank=True)
	province = models.TextField(blank=True)
	municipality = models.TextField(blank=True)
	phone_number = models.TextField(max_length=7, blank=True)
	
	def __str__(self):
		return u'%s, %s' % (self.user.last_name, self.user.first_name)

	def role(self):
		if len(Teacher.objects.filter(user_id = self.user.id)) > 0:
			return 'TEACHER'
		elif len(Student.objects.filter(user_id = self.user.id)) > 0:
			return 'STUDENT'
		elif len(Admin.objects.filter(user_id = self.user.id)) > 0 or len(SUadmin.objects.filter(user_id = self.user.id)) > 0:
			return 'ADMIN'

class SUadmin(models.Model):
	user = models.ForeignKey(User, related_name='self_userid')
	registered_by = models.ForeignKey(User, related_name='registered_by')
	status = models.IntegerField(default=0) # -2 deleted -1:deactivated	0:for activation (default)	1:active 
	date_added = models.DateTimeField(null=True)
	date_registered = models.DateTimeField(default=timezone.now())
	activation_code = models.CharField(max_length=32, unique=True)
	activation_code_expiry = models.DateTimeField()

	def is_activation_code_expired(self):
		delta = self.activation_code_expiry - timezone.now()
		if delta.days < 0:
			return True
		else:
			return False

	def __str__(self):
		return u'%s, %s' % (self.user.last_name, self.user.first_name)

class School(models.Model):
	name = models.CharField(max_length=100)
	short_name = models.CharField(max_length=20)
	address = models.TextField()
	key = models.CharField(max_length=32)
	suadmin = models.ForeignKey(SUadmin,blank=True, null=True)
	date_created = models.DateTimeField(default=datetime.now)
	is_active = models.IntegerField(default=0)

	def __str__(self):
		return u'%s (%s)' % (self.name, self.short_name)

	class Meta:
		ordering = ['name']

class Teacher(models.Model):
	user = models.ForeignKey(User)
	school = models.ManyToManyField(School, blank=True, null=True)
	
	def __str__(self):
		return u'%s, %s' % (self.user.last_name, self.user.first_name)

class Student(models.Model):
	user = models.ForeignKey(User)
	school = models.ForeignKey(School, blank=True, null=True)

	def __str__(self):
		return u'%s, %s' % (self.user.last_name, self.user.first_name)


class Admin(models.Model):
	user = models.ForeignKey(User)
	school = models.ForeignKey(School, blank=True, null=True)

	def __str__(self):
		return u'%s, %s' % (self.user.last_name, self.user.first_name)

class passwordForm(ModelForm):
	class Meta:
		model = User
		exclude = ('last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined')
		widgets = {
			'password': PasswordInput(attrs={'class':'span3', 'name':'newPassword', 'placeholder':'Required'}),
			'confirm_password': PasswordInput(attrs={'class':'span3', 'name':'newPassword', 'placeholder':'Required'}),
		}
