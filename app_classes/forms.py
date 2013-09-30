from django import forms
import re
from django.core.validators import validate_email

class MultiEmailField(forms.Field):
    def to_python(self, value):
        "Normalize data to a list of strings."

        # Return an empty list if no input was given.
        if not value:
            return []
        return re.split(',\s+', value)

    def validate(self, value):
        "Check if value consists only of valid emails."

        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)

        for email in value:
            validate_email(email)

class MailForm(forms.Form):
	emails = MultiEmailField(label="Email", required=False, widget=forms.Textarea(attrs={'class':'span3'}))

	def cleaned_emails(self):
		data = self.cleaned_data.get('emails', [])
		return data.split(',')

class MailForm2(forms.Form):
    emails = MultiEmailField(label="Email", required=True, widget=forms.Textarea(attrs={'class':'span3'}))

    def cleaned_emails(self):
        data = self.cleaned_data.get('emails', [])
        return data.split(',')