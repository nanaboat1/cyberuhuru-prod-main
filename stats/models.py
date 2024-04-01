# import cv2
from django.conf import settings
from django.db import models
import datetime
from ckeditor.fields import RichTextField

from users.models import BaseModel
from users.models import User
from django.utils import timezone

class VistorContact(models.Model):
    first_name = models.CharField(max_length=25, null=True, blank=True)
    last_name = models.CharField(max_length=25, null=True, blank=True)
    email_id = models.EmailField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Visitor Contact"   

    def __str__(self):
        return self.first_name


class HomeVideos(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    video_url = models.CharField(max_length=500, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = 'Home Video'
        verbose_name_plural = 'Home Video'

    def __str__(self):
        return self.title


class Course(models.Model):
    course_title = models.CharField(max_length=100, null=True, blank=True)
    course_vid = models.FileField(upload_to='videos/', null=True, blank=True)
    video_url = models.CharField(max_length=500, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='uploads/', null=True, blank=True)
    course_content = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Course Page'

    def __str__(self):
        return self.course_title

    def course_duration(self):
        seconds = 0 
        try:
            course_vid = self.course_video.all()
            for videos in course_vid:
                # data = cv2.VideoCapture(str(settings.BASE_URL) + videos.video.url)
                # frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
                # fps = int(data.get(cv2.CAP_PROP_FPS))
                # seconds += int(frames / fps)
                seconds += videos.duration.seconds
            video_time = str(datetime.timedelta(seconds=seconds))
        except:
            video_time = str(datetime.timedelta(seconds=seconds))
        return video_time

    def chapters_count(self):
        count = 0 
        count = self.course_video.count()
        return count
        
class CourseVideos(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    video_url = models.CharField(max_length=500, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    content = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    courses = models.ForeignKey(
        'Course', on_delete=models.CASCADE, related_name='course_video', null=True)

    class Meta:
        verbose_name = 'Course Chapters'
        verbose_name_plural = 'Course Chapters'

    def __str__(self):
        return f'{str(self.courses)} - {self.title}'


class Home(models.Model):
    company_logo = models.ImageField(
        upload_to='uploads/', null=True, blank=True)
    content = RichTextField(null=True, blank=True)
    titles = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "Home Carousel"

    def __str__(self):
        return self.titles


class Welcome(models.Model):
    content = RichTextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "Welcome"

    def __str__(self):
        return self.title


class About(models.Model):
    content = RichTextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "About Page"

    def __str__(self):
        return self.title


class CompanyAddress(models.Model):
    company_address = models.CharField(max_length=555, null=True, blank=True)
    contact_number = models.BigIntegerField(blank=True, null=True)
    email_address = models.EmailField(
        max_length=255, unique=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "Company Address"

    def __str__(self):
        return f'{self.company_address}'


class Newsletter(models.Model):
    content = RichTextField(null=True, blank=True)
    titles = models.TextField(null=True, blank=True, default='Our Newsletter')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "Our Newsletter"

    def __str__(self):
        return self.content


class TermsConditions(models.Model):
    terms_condations = models.CharField(max_length=55, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "Terms & Conditions"

    def __str__(self):
        return self.terms_condations


class Countries(models.Model):
    sortname = models.CharField(max_length=3, null=True, blank=True)
    phone_code = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.country


class State(models.Model):
    state = models.CharField(max_length=150, blank=True, null=True)
    country = models.ForeignKey(
        'Countries', on_delete=models.CASCADE, related_name='state')

    def __str__(self):
        return self.state


class Cities(models.Model):
    city = models.CharField(max_length=150, blank=True, null=True)
    state = models.ForeignKey(
        'State', on_delete=models.CASCADE, related_name='city')

    def __str__(self):
        return self.city


class Industry(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Messages(models.Model):
    sender = models.CharField(max_length=400, null=True, blank=True, default='Grandmas House <noreply@sourcesoftsolutions.com>')
    receiver = models.CharField(max_length=400, null=True, blank=True)
    subject = models.TextField(null=True, blank=True, default='Our Newsletter')
    text = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name_plural = "Message" 

    def __str__(self):
        return self.sender


class Test(BaseModel):
    name = models.CharField(max_length=255)
    duration = models.DurationField()
    no_of_questions = models.IntegerField()
    pass_percentage = models.IntegerField()
    instructions = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name='course_test')
    
    class Meta:
        verbose_name_plural = 'Course Tests'

    def __str__(self):
        return f'{str(self.course)} - {self.name}'


class Questions(BaseModel):
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    test = models.ForeignKey('Test', on_delete=models.CASCADE, null=True, related_name='test_question')

    class Meta:
        verbose_name_plural = 'Test Questions '

    def __str__(self):
        return f'{self.test}: Question-{self.id}'

class AnswerChoices(BaseModel):
    content = models.CharField(max_length=255)
    question = models.ForeignKey('Questions', on_delete=models.CASCADE, related_name='question_choices')

    class Meta:
        verbose_name_plural = 'Test Question Choices'

    def __str__(self):
        id = self.id
        if id>4:
            if id%4==1:
                id = 1
            elif id%4==2:
                id = 2
            elif id%4==3:
                id = 3
            elif id%4==0 and id != 4:
                id = 4
        return f'{self.question} || Option:({id})'

class Blog(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title