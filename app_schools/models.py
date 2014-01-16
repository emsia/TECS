from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from app_auth.models import School, SUadmin, Admin
from django.forms.widgets import TextInput, Select, SelectMultiple, Textarea
from datetime import datetime

class School(models.Model):
	name = models.CharField(max_length=100)
	short_name = models.CharField(max_length=20)
	address = models.TextField()
	suadmin = models.ForeignKey(SUadmin)
	admin = models.ManyToManyField(Admin, related_name="ad")
	key = models.CharField(max_length=32)
	date_created = models.DateTimeField(default=datetime.now)
	is_active = models.IntegerField(default=0)

	def __str__(self):
		return u'%s (%s)' % (self.name, self.short_name)

class SchoolForm(ModelForm):
	class Meta:
		model = School
		exclude = ('suadmin', 'key', 'date_created', 'is_active', 'admin')
		widgets = {
		  'name': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'name' }),
          'short_name': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'short_name'}),
          'address': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'address'})
           }

        def cleaned_Emails(self):
        	data = self.cleaned_data.get('Emails', [])
        	return data.split(',')

class EditForm(ModelForm):
	class Meta:
		model = School
		exclude = ('suadmin', 'key', 'date_created', 'is_active', 'admin')
		widgets = {
		  'name': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'name' }),
          'short_name': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'short_name'}),
          'address': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'address'})
        }
