
from django.contrib.auth.models import User
from app_auth.models import School
from django import forms
from decimal import Decimal
import re

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'type':'text', 'class': 'login-field', 'placeholder': 'Username', 'autofocus':'autofocus', 'autocomplete':'off'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'login-field', 'placeholder':'Password'}))

class PasswordForm(forms.Form):
	OldPassword = forms.CharField( label='Old Password', widget=forms.PasswordInput(attrs={'type':'password', 'class': 'span3', 'placeholder': 'Required', 'name': 'newPassword'}))
	password = forms.CharField( label='Password', widget=forms.PasswordInput(attrs={'type':'password', 'class': 'span3', 'placeholder': 'Required', 'name': 'newPassword'}))
	ConfPassword = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'type':'password', 'class': 'span3', 'placeholder': 'Required', 'name':'confPassword'}))

class ProfileForm(forms.Form):
	last_name = forms.CharField( label='Last Name', widget=forms.TextInput(attrs={'type':'text', 'class': 'span3 cap', 'placeholder': 'Required', 'style':'color: #099'}))
	first_name = forms.CharField( label='First Name', widget=forms.TextInput(attrs={'type':'text', 'class': 'span3 cap', 'placeholder': 'Required', 'style':'color: #099'}))
	username = forms.CharField( label='Username', widget=forms.TextInput(attrs={'type':'text', 'class': 'span3', 'placeholder': 'Required', 'style':'color: #099'}))
	email = forms.CharField( label='Email', widget=forms.TextInput(attrs={'type':'text', 'class': 'span3', 'placeholder': 'Required', 'style':'color: #099'}))
	street = forms.CharField( label='Street', required=False, widget=forms.TextInput(attrs={'type':'text', 'class cap': 'span3', 'placeholder': 'Optional'}))
	municipality = forms.CharField( label='Municipality', required=False, widget=forms.TextInput(attrs={'type':'text', 'class': 'span3 cap', 'placeholder': 'Optional'}))
	province = forms.CharField( label='Province', required=False, widget=forms.TextInput(attrs={'type':'text', 'class': 'span3 cap', 'placeholder': 'Optional'}))
	phone_number = forms.CharField( label='Phone Number', required=False, widget=forms.TextInput(attrs={'type':'text', 'class': 'span3', 'placeholder': 'Optional'}))
	avatar = forms.ImageField(label='Avatar', required=False, widget=forms.ClearableFileInput(attrs={'type':'file', 'class':'filestyle span3'}))

class schoolForAll(forms.Form):
	school = forms.CharField(label='School', widget=forms.TextInput(attrs={'type':'text', 'class':'span12 cap disabled', 'style':'color: #099', 'disabled':True}))

class GradeForm_Option1(forms.Form):
	grades = forms.CharField(max_length=1024, widget=forms.TextInput(attrs={'class':'tagsinput', 'style':'display: none;' }))

	def clean_grades(self):
		grades = self.cleaned_data['grades']
		num_input = len(grades.split(','))
		if num_input < 2:
			raise forms.ValidationError("Enter at least 2 grade values.")
		return grades

class GradeForm_Option2(forms.Form):
	start = forms.FloatField(widget=forms.TextInput(attrs={'class':'span1'}))
	end = forms.FloatField(widget=forms.TextInput(attrs={'class':'span1'}))
	step = forms.FloatField(widget=forms.TextInput(attrs={'class':'span1'}))

	def clean_step(self):
		clean_start = self.cleaned_data['start']
		clean_end = self.cleaned_data['end']
		clean_step = self.cleaned_data['step']

		if Decimal(str(clean_end - clean_start + 1))%Decimal(str(clean_step)) != Decimal('0.0'):
			raise forms.ValidationError("Using this interval won't reach the last possible grade value.")
		return clean_step

class NewSuperAdminForm(forms.Form):
	username = forms.CharField(widget=forms.TextInput(attrs={'type':'text', 'class':'span1', 'autofocus':'autofocus', 'autocomplete':'off'}))
	last_name =  forms.CharField(widget=forms.TextInput(attrs={'type':'text', 'class':'span1', 'autocomplete':'off'}))
	first_name =  forms.CharField(widget=forms.TextInput(attrs={'type':'text', 'class':'span1', 'autocomplete':'off'}))
	email =  forms.EmailField(widget=forms.TextInput(attrs={'type':'text', 'class':'span1', 'autocomplete':'off'}))

	def clean_username(self):
		username = self.cleaned_data['username']
		if len(username) < 4 or len(username) > 30:
			raise forms.ValidationError("Username must be between 4 and 30 characters.")
		elif re.match(r'^[A-Za-z0-9]+(?:[_]?[A-Za-z0-9]+)?$', username) is None:
			raise forms.ValidationError("Please use only letters (A-Z, a-z), numbers and an underscore.")
		elif User.objects.filter(username__iexact=username).exists():			
			raise forms.ValidationError("This username is taken.")
		else:
			return username