"""
Python file to create models for User realated
"""
# python Imports
import os
from dateutil.relativedelta import relativedelta

# Django Imports
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.enums import Choices

# Users imports
from users.managers import UserManager
from users.constants import(HIGHEST_QUALIFICATION_CHOICES, COURSE_TYPE_CHOICES, PASSING_OUT_YEAR_CHOICES,
	EDUCATION_TYPE_CHOICES)


class User(AbstractBaseUser):
	first_name = models.CharField(max_length=25, blank=True, null=True)
	last_name = models.CharField(max_length=25, blank=True, null=True)
	email_id = models.EmailField(
	    max_length=255, unique=True, blank=False, null=False)
	password = models.CharField(max_length=255, blank=True, null=True)
	username = models.CharField(max_length=25, unique=True, blank=True, null=True)
	phone_number = models.CharField(max_length=25, blank=True, null=True)
	is_active = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	is_candidate_user = models.BooleanField(default=False)
	is_company_user = models.BooleanField(default=False)
	is_prime = models.BooleanField(default=False)
	disable_send = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
	cancel_membership = models.BooleanField(default=False)
	profile_photo = models.ImageField(upload_to='uploads/', null=True, blank=True)
	token = models.CharField(max_length=4096, null=True, blank=True)
	uid = models.CharField(max_length=4096, null=True, blank=True)
	is_aragreement = models.BooleanField(default=False)

	USERNAME_FIELD = 'email_id'
	REQUIRED_FIELDS = []

	objects = UserManager()

	class Meta:
		verbose_name = 'user'

	def __str__(self):
		return self.email_id

	def has_perm(self, perm, obj=None):
		# Simplest possible answer: Yes, always
		return True

	def has_module_perms(self, app_label):
		# Simplest possible answer: Yes, always
		return True

	@property
	def is_staff(self):
		# Simplest possible answer: All admins are staff
		return self.is_admin

	@property
	def profile_percentage(self):
		percentage = 30

		if self.profile_photo is not None:
			percentage += 10
		if self.address.exists():
			percentage += 20
		if self.educational.exists():
			percentage += 20
		if self.experience.exists():
			percentage += 20
		return str(percentage) + '%'

	def experience_in_years(self):
		years = 0.0
		if self.experience.exists():
			experiences = self.experience.all()
			for experience in experiences:
				diff = relativedelta(experience.end_date, experience.joining_date)
				years += diff.years + diff.months/10
		return years

	def current_designation(self):
		designation = None
		if self.experience.exists():
			latest_experience = self.experience.latest('end_date')
			designation = latest_experience.designation
		return designation


class Address(models.Model):
	address = models.CharField(max_length=255, null=True, blank=True)
	country = models.ForeignKey(
	    'stats.Countries', on_delete=models.CASCADE, null=True, blank=True)
	state = models.ForeignKey(
	    'stats.State', on_delete=models.CASCADE, null=True, blank=True)
	city = models.ForeignKey(
	    'stats.Cities', on_delete=models.CASCADE, null=True, blank=True)
	zip_code = models.CharField(max_length=255, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
	user = models.ForeignKey('User', on_delete=models.CASCADE,
	                         related_name='address', null=True)

	class Meta:
		verbose_name = 'Address Detail'
		verbose_name_plural = 'Address Details'

	def __str__(self):
		return f'{str(self.user)} - {self.address}'


class CandidateSkills(models.Model):
	skill = models.ForeignKey(
	    'Skills', on_delete=models.CASCADE, related_name='skill', null=True)
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
	user = models.ForeignKey('User', on_delete=models.CASCADE,
	                         related_name='user_skills', null=True)

	def __str__(self):
		return f'{str(self.user)}({self.skill})' 

class EducationDetails(models.Model):
	highest_qualification = models.CharField(max_length=30, choices=HIGHEST_QUALIFICATION_CHOICES)
	institute = models.CharField(max_length=255, blank=True, null=True)
	course_type = models.CharField(max_length=30, choices=COURSE_TYPE_CHOICES)
	passing_out_year = models.CharField(max_length=5, choices=PASSING_OUT_YEAR_CHOICES)
	education_type = models.CharField(max_length=15, choices=EDUCATION_TYPE_CHOICES)
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
	user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='educational', null=True)

	class Meta:
		verbose_name = 'Educational Detail'
		verbose_name_plural = 'Educational Details'

	def __str__(self):
		return f'{str(self.user)}({self.course_type})' 


class Experience(models.Model):
	company_name = models.CharField(max_length=255, null=True, blank=True)
	designation = models.CharField(max_length=255, null=True, blank=True)
	currently_working =  models.CharField(max_length=255, null=True, blank=True)
	joining_date = models.DateField(auto_now_add=False, auto_now=False)
	end_date = models.DateField(auto_now_add=False, auto_now=False)
	skills = models.CharField(max_length=255, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
	user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='experience', null=True)

	class Meta:
		verbose_name = 'Experience Details'
		verbose_name_plural = 'Experience Details'

	def __str__(self):
		return f'{str(self.user)}({self.company_name})'


class Resume(models.Model):
	resume = models.FileField(null=True, blank=True,upload_to='files')
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
	user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='resume', null=True)

	class Meta:
		verbose_name = 'Candidate Resume'
		verbose_name_plural = 'Candidate Resumes'

	def __str__(self):
		return f'{str(self.user)}(resumes)'


class Skills(models.Model):
	name = models.CharField(max_length=50)
	default = models.CharField(max_length=5)

	class Meta:
		verbose_name = 'Defualt Skill'
		verbose_name_plural = 'Default Skills'
		
	def __str__(self):
		return self.name

	
class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Agreement(BaseModel):
	document = models.FileField(blank=True, null=True, upload_to='files')
	signed_document = models.FileField(blank=True, null=True, upload_to='files')
	user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='candidate_agreement', null=True)
	
	def __str__(self):
		return f'{str(self.user)}(agreement)'
	
	def signed_doc_filename(self):
		return os.path.basename(self.signed_document.name)


class Training(BaseModel):
	user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, related_name="candidate_training")
	course = models.ForeignKey('stats.Course', on_delete=models.CASCADE, related_name='training', null=True)
	is_completed = models.BooleanField(default=0)
	
	class Meta:
		verbose_name = 'Candidate Training'
		verbose_name_plural = 'Candidate Training'
		
	def __str__(self):
		return f'{str(self.user)} - {str(self.course)}'

	def remainingEpisodes(self):
		episodes_count = self.training_videos.filter(progress_percentage__gte=99, progress_percentage__lte=100).count()
		course_episodes_count = self.course.course_video.count()
		return course_episodes_count - episodes_count


class Trainingvideos(BaseModel):
	training = models.ForeignKey(
							'Training', 
							on_delete=models.CASCADE,
							related_name="training_videos" 
	)
	episode = models.ForeignKey(
							'stats.CourseVideos',
							on_delete=models.CASCADE,
							related_name='course_training_videos'
	)
	progress_percentage = models.PositiveIntegerField(default=0)


	class Meta:
		managed = True
		unique_together = (("training", "episode"),)

	def __str__(self):
		return str(self.id)


class Test(BaseModel):
	test = models.ManyToManyField('stats.Test')
	training = models.ForeignKey('Training', on_delete=models.CASCADE, related_name="training_user_test")
	time_taken = models.CharField(max_length=255, blank=True, null=True)
	is_submitted = models.BooleanField(default=False)
	percentage_attained = models.IntegerField(blank=True, null=True)

	class Meta:
		verbose_name = 'Candidate Test'
		verbose_name_plural = 'Candidate Tests'
		
	def __str__(self):
		return str(self.test)


class TestAnswer(BaseModel):
	question = models.ForeignKey('stats.questions', on_delete=models.CASCADE)
	answer = models.CharField(max_length=255)
	user_test = models.ForeignKey('Test', on_delete=models.CASCADE, blank=True, null=True, related_name='UserTest')
	user = models.ForeignKey('User', on_delete=CASCADE, blank=True, null=True)

	class Meta:
		verbose_name = 'Candidate Test Q&A'
		verbose_name_plural = 'Candidate Test (Q&A)s'
		
	def __str__(self):
		return f'{str(self.user)} - Q:{str(self.user_test)}'


class Certificate(BaseModel):
    training = models.OneToOneField('Training', on_delete=models.CASCADE, related_name="training_certificate")
    file = models.FileField(blank=True, null=True, upload_to='files/certificate')
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    
    def __str__(self):
        return str(self.id)
