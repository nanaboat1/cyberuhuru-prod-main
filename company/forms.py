# Python Imports
from datetime import datetime, date
import re

# Django Imports
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models.enums import Choices
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import password_changed, validate_password
from django.utils import timezone

# User relayted import
from users.models import User
from users.constants import  SKILLS, NUMBER_OF_EMPLOYEES
from company.models import Advertisement

class CompanyRegistrationForm(forms.Form):
	'''
	Form to register User as Company, there are fields that are required... 
	'''

	company_name = forms.CharField(required=True,
		error_messages ={'required':'Please Enter Company Name.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
		)

	email_id = forms.CharField(required=True,
		error_messages ={'required':'Please Enter Email ID.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
		)
	address = forms.CharField(required=True,
		error_messages={'required':'Please Enter Address.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
		)

	phone_number = forms.CharField(required=True,
		error_messages ={'required':'Please Enter Phone number.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
		)
	country 		 = forms.CharField(required=True)
	state 		  	 = forms.CharField(required=True)
	city 		 	 = forms.CharField(required=True)
	industry         = forms.IntegerField(required=True,
		error_messages={'required':'Please Select Industry.. '})
	establish_at   = forms.DateField(required=True)

	def clean_email_id(self):
		'''
		Validation for Email Id
		'''
		email_id = self.cleaned_data['email_id']

		if User.objects.filter(email_id__iexact=email_id).exists():
			print("Email already exists")
			raise forms.ValidationError("This Email already exists!")
		else:
			return email_id

	def clean_phone_number(self):
		'''
		validation For Phone Number
		'''
		phone_number = self.cleaned_data.get('phone_number')
		if len(phone_number) !=10:
			raise forms.ValidationError("Phone Number length should be 10")
		
		pattern = re.compile("[0-9]{10}")
		if pattern.match(phone_number) is None:
			raise forms.ValidationError("Please enter valid Contact number")

		return phone_number

	def clean_establish_at(self):
		establish_at = self.cleaned_data.get('establish_at')

		if (datetime.combine(establish_at, datetime.min.time())) > datetime.now():
			raise forms.ValidationError("Invalid date")
		else:
			return establish_at


class CompanyLogin(forms.Form):

	email_id = forms.EmailField(required=True,
		error_messages={'required':'Please Enter Email Address'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	password = forms.CharField(required = True,
		error_messages={'required':'Please Enter Password'}
	)


class CompanyForgotPassword(forms.Form):

	email_id = forms.EmailField(required=True) 

	def clean_email_id(self):
		email_id = self.cleaned_data['email_id']
	
		if not User.objects.filter(email_id__iexact=email_id).exists():
			raise forms.ValidationError("Record not found.")

		return email_id


class CompanyProfileForm(forms.Form):
	company_name = forms.CharField(required=True)
	email_id = forms.EmailField(required=True)
	
	phone_number = forms.CharField(required=False)
	country = forms.CharField(required=False)
	state= forms.CharField(required=False)
	city = forms.CharField(required=False)
	industry = forms.CharField(required=False)
	establish_at = forms.DateField(required=False)

	def clean_phone_number(self):
		'''
		validation For Phone Number
		'''
		phone_number = self.cleaned_data.get('phone_number')
		if len(phone_number) !=10:
			raise forms.ValidationError("Phone Number length should be 10")
		
		pattern = re.compile("[0-9]{10}")
		if pattern.match(phone_number) is None:
			raise forms.ValidationError("Please enter valid Contact number")

		return phone_number


class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(required=True)
	new_password = forms.CharField(required=True)
	confirm_new_password = forms.CharField(required=True)


	def clean_confirm_new_password(self):
		new_password = self.cleaned_data.get('new_password')
		confirm_new_password = self.cleaned_data.get('confirm_new_password')
		
		if confirm_new_password != new_password:
			raise forms.ValidationError("New Password & Confirm New Password should be same.") 

		pattern  = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$')
		if pattern.match(confirm_new_password) is None:
			raise forms.ValidationError("Password format is not correct")

		return confirm_new_password

	
class HireCandidateForms(forms.Form):
	number_of_employees = forms.ChoiceField(choices=NUMBER_OF_EMPLOYEES)#required=True)
	technology = forms.ChoiceField(choices=SKILLS)


class CompanyResetPasswordForm(forms.Form):
	password = forms.CharField(required=True)
	confirm_password = forms.CharField(required=True)

	def clean_password(self):
		regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
		pattern = re.compile(regex)
		password = self.cleaned_data.get('password')

		match = re.search(pattern, password)

		if match and len(password)>=8:
			return password
		else:
			raise forms.ValidationError("Password should contains(1- lower case, 1- upper_case and 1-special character, atlease 8 character)")


class AdvertisementForm(forms.ModelForm):
    job_title = forms.CharField(max_length=255, required=True)
    workplace_title = forms.CharField(max_length=100)
    job_location = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=255)
    description_of_job = forms.CharField(max_length= 255)
    filter = forms.CharField(max_length=150)
  
    class Meta:  
        managed = False
        model = Advertisement  
        fields = "__all__"
        
    