from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from app_auth.models import School, Student, Teacher
from django.forms.widgets import TextInput, Select, SelectMultiple, Textarea
from datetime import datetime

class Class(models.Model):
	school = models.ForeignKey(School)
	year_level = models.CharField(max_length=10)
	section = models.CharField(max_length=30)
	subject = models.CharField(max_length=30)
	academic_year = models.CharField(max_length=20)
	teacher = models.ForeignKey(Teacher)
	student = models.ManyToManyField(Student)
	key = models.CharField(max_length=32)
	date_created = models.DateTimeField(default=datetime.now)
	is_active = models.IntegerField(default=0)

	def save(self):
		self.year_level = self.year_level.upper()
		super(MyModel, self).save()

	def __str__(self):
		return u'%s-%s %s' % (self.year_level, self.section, self.subject)

class ClassForm(ModelForm):
	class Meta:
		model = Class
		exclude = ('teacher', 'key', 'date_created', 'is_active', 'student', 'school')
		widgets = {
          'year_level': TextInput(attrs={'class':'input-xlarge span11 cap', 'data-name':'year_level' }),
          'section': TextInput(attrs={'class':'input-xlarge span11 cap', 'data-name':'section'}),
          'subject': TextInput(attrs={'class':'input-xlarge span11 cap'}),
          'academic_year': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'academic_year'}),
        }

        def cleaned_Emails(self):
        	data = self.cleaned_data.get('Emails', [])
        	return data.split(',')

class EditForm(ModelForm):
	class Meta:
		model = Class
		exclude = ('teacher', 'key', 'date_created', 'is_active', 'student', 'school')
		widgets = {
			'year_level': TextInput(attrs={'class':'input-xlarge span4 cap', 'data-name':'year_level' }),
			'section': TextInput(attrs={'class':'input-xlarge span4 cap', 'data-name':'section'}),
			'subject': TextInput(attrs={'class':'input-xlarge span4 cap', 'data-name':'subject'}),
			'academic_year': TextInput(attrs={'class':'input-xlarge span4', 'data-name':'academic_year'}),
		}

class EnrollForm(ModelForm):
	class Meta:
		model = Class
		fields = ['key']
		widgets = {
			'key': TextInput(attrs={'class':'input-xlarge span2', 'data-name':'key'}),
		}

class EditForm_admin(ModelForm):
	class Meta:
		model = School
		exclude = ('suadmin', 'key', 'date_created', 'is_active', 'admin')
		widgets = {
		  'name': TextInput(attrs={'class':'input-xlarge span11 cap', 'data-name':'name' }),
          'short_name': TextInput(attrs={'class':'input-xlarge span11 cap', 'data-name':'short_name'}),
          'address': TextInput(attrs={'class':'input-xlarge span11 cap', 'data-name':'address'})
        }