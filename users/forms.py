import re
from django import forms
from django.core import validators
from django.db import models
from django.db.models import fields
from django.db.models.enums import Choices
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password
# from django.forms import ModelForm  

from users.models import EducationDetails, User, Resume, Experience, Skills
from users.constants import( HIGHEST_QUALIFICATION_CHOICES, COURSE_TYPE_CHOICES, PASSING_OUT_YEAR_CHOICES,
	EDUCATION_TYPE_CHOICES, SKILLS)

class UserChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = User
		fields = ('username', 'password', 'is_active', 'is_admin')

	def clean_password(self):
		# Regardless of what the user provides, return the initial value.
		# This is done here, rather than on the field, because the
		# field does not have access to the initial value
		return self.initial["password"]


class SignUpForm(forms.Form):
	'''
	Cadidate registration Form 
	'''
	first_name = forms.CharField(
		max_length=25,
		required=True,
		error_messages={'required':'Please Enter First Name.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	last_name = forms.CharField(
		max_length=25,
		required=True,
		error_messages={'required':'Please Enter First Name.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	
	email_id = forms.EmailField(required=True,
		error_messages={'required':'Please Enter Email Address'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	password = forms.CharField(required=True,
		error_messages={'required':'Please Enter Password'},
		widget=forms.PasswordInput,validators=[validate_password])

	confirm_password = forms.CharField(required=True,
		error_messages={'required':'Please Enter Confirm Password'}, 
		widget=forms.PasswordInput,validators=[validate_password]
	)
	phone_number =  forms.CharField(
		# region='US',
		required=True,
		error_messages={'required':'Please Enter Contact Number'},
		# widget=forms.TextInput(attrs={'class':'form-control'})
	)
	address = forms.CharField(required=False)
	country = forms.CharField(required=False)
	state = forms.CharField(
		max_length=25,
		required=True,
		error_messages={'required':'Please Enter State Name.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	city = forms.CharField(
		max_length=25,
		required=True,
		error_messages={'required':'Please Enter City Name.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	is_aragreement = forms.CharField(required=False)
	
	def clean_email_id(self):
		'''
		Validation for Email id
		'''
		email_id = self.cleaned_data['email_id']
		
		if User.objects.filter(email_id__iexact=email_id).exists():
			print("Email already exists")
			raise forms.ValidationError("This Email already exists!")
			
		return email_id

	def clean_confirm_password(self):
		'''
		validation to match Password and Confirm Password
		'''
		data = self.cleaned_data
		password = self.cleaned_data.get('password')
		confirm_password = self.cleaned_data.get('confirm_password')

		if confirm_password != password:
			raise forms.ValidationError("Password & Confirm Password must be same.") 

		return confirm_password

	
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
	 
	


class LoginForm(forms.Form):
	'''
	Candidate login form 
	'''
	email_id = forms.EmailField(required=True,
		error_messages={'required':'Please Enter Email Address'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	password = forms.CharField(required=True,
		error_messages={'required':'Please Enter Password'},
		widget=forms.PasswordInput,validators=[validate_password]
	)
	
	def clean_email_id(self):
		'''
		Email Validation Method
		'''
		email_id = self.cleaned_data['email_id']
	
		if not User.objects.filter(email_id__iexact=email_id).exists():
			raise forms.ValidationError("This Email is not registered!")
		else:
			return email_id
	
	def clean_password(self):
		'''
		password Validation Method
		'''

		password = self.cleaned_data['password']
		print("password", password)
		if len(password) < 8: 
			print("password",len(password))
			raise forms.ValidationError("Incorrect Password!!")
		else:
			return password
	

class ProfileForm(forms.Form):
	'''
	Candidate Profile Form
	'''

	first_name = forms.CharField(
		max_length=25,
		required=True,
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	last_name = forms.CharField(
		max_length=25,
		required=False,
		error_messages={'required':'Please Enter First Name.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	phone_number = forms.CharField(
		required=False,
		error_messages={'required':'Please Enter Contact Number'}
	)
	email_id = forms.EmailField(required=True,
		error_messages={'required':'Please Enter Email Address'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)

	country = forms.IntegerField(required=False)

	state = forms.IntegerField(
		required=False,
		error_messages={'required':'Please Select state first..'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	city = forms.CharField(
		required=False,
		error_messages={'required':'Please select City first'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)

	def clean_phone_number(self):
		'''
		validation For Phone Number
		'''
		phone_number = self.cleaned_data.get('phone_number')
		if len(phone_number) !=10:
			raise forms.ValidationError("Phone Number length should be 10")
		else:
			return phone_number

class ProfileImage(forms.Form):
	# class Meta:	
	# 	model = User
	# 	fields = ['profile_photo']

	profile_photo = forms.FileField(required=True)


class UserForgotPassword(forms.Form):
	email_id = forms.CharField(required=True)

	def clean_email_id(self):
		print("\n\nInside clean_email_id function of  user forgotpassword form")
		email_id = self.cleaned_data['email_id']
	
		if not User.objects.filter(email_id__iexact=email_id).exists():
			print("Email is not registered")
			raise forms.ValidationError("Record not found.")

		return email_id


class ResetPasswordForm(forms.Form):
	password = forms.CharField(
		required=True,
		error_messages={'required':'Please Enter Password'},
		widget=forms.PasswordInput,validators=[validate_password])

	confirm_password = forms.CharField(
		required=True,
		error_messages={'required':'Please Re-enter your password to confirm'}, 
		widget=forms.PasswordInput,validators=[validate_password]
	)
	
	def clean_reset_password(self):
		
		data = self.cleaned_data
		new_password = self.cleaned_data.get('new_password')
		confirm_password = self.cleaned_data.get('confirm_new_password')
		
		if confirm_password != new_password:
			raise forms.ValidationError("New Password & Confirm New Password should be same.") 
		elif len(confirm_password) < 8: 
			print("password",len(confirm_password))
			raise forms.ValidationError("Incorrect Password!!")
		else:
			return confirm_password

		return confirm_password


class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(required=True,
		error_messages={'required':'Please Enter Confirm Password'}, 
		widget=forms.PasswordInput,validators=[validate_password]
	)
	new_password = forms.CharField(required=True,
		error_messages={'required':'Please Enter Password'},
		widget=forms.PasswordInput,validators=[validate_password]
	)

	confirm_new_password = forms.CharField(required=True,
		error_messages={'required':'Please Enter Confirm Password'}, 
		widget=forms.PasswordInput,validators=[validate_password]
	)

	def clean_confirm_new_password(self):
		
		data = self.cleaned_data
		new_password = self.cleaned_data.get('new_password')
		confirm_new_password = self.cleaned_data.get('confirm_new_password')
		
		if confirm_new_password != new_password:
			raise forms.ValidationError("New Password & Confirm New Password should be same.") 
		elif len(confirm_new_password) < 8: 
			print("password",len(confirm_new_password))
			raise forms.ValidationError("Incorrect Password!!")
		else:
			return confirm_new_password

		return confirm_new_password


class ProfileImage(forms.ModelForm):
	class Meta:	
		model = User
		fields = ['profile_photo']

	# profile_photo = forms.FileField(required=True)


class UploadResumeForm(forms.Form):
	resume = forms.FileField(widget=forms.FileInput(attrs={'accept':'application/pdf'}))

	def clean(self):
		uploaded_resume = self.cleaned_data
		pdf = uploaded_resume.get('resume', None)
		if pdf is not None:
			main, sub = pdf.content_type.split('/')
			print("sub ===========", sub, main)
			docx = "vnd.openxmlformats-officedocument.wordprocessingml.document"
			doc = "msword"
            # main here would most likely be application, as pdf mime type is application/pdf, 
            # but I'd like to be on a safer side should in case it returns octet-stream/pdf
			if not (main in ["application", "octet-stream"] and (sub == "pdf" or sub == docx or sub == doc)):
				print("Please use a PDF file")
				raise forms.ValidationError(u'Please use a PDF file')
		return uploaded_resume


class ExperienceForm(forms.Form):
	'''
	Form for Emplyement and give some validations on it 
	'''
	
	company_name = forms.CharField(
		max_length=25,
		required=True,
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	designation = forms.CharField(
		max_length=25,
		required=True,
		error_messages={'required':'Please Enter First Name.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	currently_working = forms.BooleanField(
		required=False,
		# widget=forms.TextInput(attrs={'class':'form-control'})
	)
	joining_date = forms.DateField(
		required=True,
		error_messages={'required':'Please Enter Joining Date'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	end_date = forms.DateField(
		required=True,
		error_messages={'required':'Please Enter end Date'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	skills = forms.CharField(
		max_length=255,
		required=True,
		error_messages={'required':'Please Enter Skills.'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)
	description = forms.CharField(
		max_length=255,
		required=True,
		error_messages={'required':'Please Enter Description'},
		widget=forms.TextInput(attrs={'class':'form-control'})
	)


class EducationForm(forms.ModelForm):
	class Meta:
		model = EducationDetails
		fields = ['highest_qualification', 'institute', 'course_type', 'passing_out_year', 'education_type']


# class SearchedSkillForm(forms.Form):
# 	searched_skill = forms.CharField()

# 	def clean_searched_skill(self):

# 		searched_skill = self.cleaned_data
	
# 		if not Skills.objects.filter(name=searched_skill['searched_skill']).exists():
# 			raise forms.ValidationError("skill not found")
		
# 		return searched_skill


class SignedAgreementForm(forms.Form):
	upload_file = forms.FileField(widget=forms.FileInput)

	def clean(self):
		uploaded_doc = self.cleaned_data
		document = uploaded_doc.get('upload_file', None)
		
		if document is not None:
			main, sub = document.content_type.split('/')
			docx = "vnd.openxmlformats-officedocument.wordprocessingml.document"
			doc = "msword"
			if not (main in ["application", "octet-stream"] and (sub == "pdf" or sub == docx or sub == doc)):
				raise forms.ValidationError('Only pdf,docx and doc file accepted')
			else:
				return uploaded_doc
		else:
			raise forms.ValidationError("File can't be null")


class AdminPasswordResetRequestForm(forms.Form):
    email_id = forms.CharField()
