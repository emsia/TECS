from django.db import models
from django.forms import ModelForm, PasswordInput
from django.conf import settings
from django.contrib.auth.models import User

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

class School(models.Model):
	name = models.CharField(max_length=100)
	short_name = models.CharField(max_length=20)
	address = models.TextField()

	def __str__(self):
		return self.name

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

class passwordForm(ModelForm):
	class Meta:
		model = User
		exclude = ('last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined')
		widgets = {
			'password': PasswordInput(attrs={'class':'span3', 'name':'newPassword', 'placeholder':'Required'}),
			'confirm_password': PasswordInput(attrs={'class':'span3', 'name':'newPassword', 'placeholder':'Required'}),
		}
