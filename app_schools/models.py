from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from app_auth.models import School, SUadmin, Admin
from django.forms.widgets import TextInput, Select, SelectMultiple, Textarea
from datetime import datetime

class SchoolForm(ModelForm):
	class Meta:
		model = School
		exclude = ('suadmin', 'key', 'date_created', 'is_active', 'admin')
		widgets = {
		  'name': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'name' }),
          'short_name': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'short_name'}),
          'address': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'address'})
           }

class EditForm(ModelForm):
	class Meta:
		model = School
		exclude = ('suadmin', 'key', 'date_created', 'is_active', 'admin')
		widgets = {
		  'name': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'name' }),
          'short_name': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'short_name'}),
          'address': TextInput(attrs={'class':'input-xlarge span11', 'data-name':'address'})
        }
