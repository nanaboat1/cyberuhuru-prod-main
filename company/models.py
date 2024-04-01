import datetime
from django.db import models
from django.utils import timezone
from stats.models import Course
from users.models import BaseModel, CandidateSkills
from users.constants import CURRENCY_CHOICES, SUBSCRIPTION_TYPE_CHOICES
from users.models import User, Training

class Company(models.Model):
    company_name = models.CharField(max_length=25, blank=True, null=True)
    industry = models.ForeignKey('stats.Industry', on_delete=models.CASCADE,
                                 related_name='company_type', null=True, blank=True)
    establish_at = models.DateField(blank=True, null=True)
    address = models.ForeignKey(
        'users.Address', on_delete=models.CASCADE, related_name='company_address', null=True)
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='company_user', null=True)
    
    def __str__(self):
        return self.company_name

    @property
    def establish_date(self):
        return self.establish_at.strftime("%Y-%m-%d")
    
    def is_subscribed(self):
        if self.user.user_subscriptions.exists():
            subscription = self.user.user_subscriptions.filter(is_paid=True, subscription__type='YEARLY')
            if len(subscription) > 0:
                latest_info = subscription.latest('created_at')
                if latest_info.end_date :
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    
    def subscription_days_remaining(self):
        if self.user.user_subscriptions.exists():
            subscription = self.user.user_subscriptions.filter(is_paid=True, subscription__type='YEARLY')

            if subscription is not None:
                latest_info = subscription.latest('created_at')
                if latest_info.end_date:
                    remaining_days = latest_info.end_date - timezone.now()
                    return remaining_days.days
                else:
                    return 0
            else:
                return 0
        else:
            return 0           


class Price(BaseModel):
    currency = models.CharField(max_length=255, null=True, blank=True, choices=CURRENCY_CHOICES)
    min_range = models.PositiveIntegerField(null=True, blank=True)
    max_range = models.PositiveIntegerField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return str(self.amount)


class Subscription(BaseModel):
    description = models.CharField(max_length=255, blank=True, null=True)
    price = models.ForeignKey('company.Price', on_delete=models.CASCADE)
    type = models.CharField(max_length=255, null=True, blank=True, choices=SUBSCRIPTION_TYPE_CHOICES)

    def __str__(self):
        return str(self.description)


class UserSubscription(BaseModel):
    subscription = models.ForeignKey('company.Subscription', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_subscriptions')
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    is_paid = models.BooleanField(default=0)
    currency = models.CharField(max_length=255, null=True, blank=True)
    resumes_limit = models.PositiveIntegerField(blank=True, null=True)
    resumes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)


class TechnolgyStack(BaseModel):
    skills = models.ForeignKey('users.Skills', on_delete=models.CASCADE)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    no_of_candidate = models.PositiveIntegerField(default=0)
    experience = models.PositiveIntegerField(default=0)
    skills_set = models.CharField(max_length=255, blank=True, null=True)
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class HireStatus(BaseModel):
    PENDING=1
    APPROVED=2
    REJECTED=3

    name = models.CharField(max_length=255)
    status_order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return str(self.id)


class HireCandidate(BaseModel):
    candidate = models.ForeignKey('users.User', related_name='hired_candidate', on_delete=models.CASCADE)
    company = models.ForeignKey('company.Company', related_name='company_hire', on_delete=models.CASCADE)
    status = models.ForeignKey('company.HireStatus', on_delete=models.CASCADE)
    approved_by = models.ForeignKey('users.User', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.id)


class ReplacementRequests(BaseModel):
    candidate = models.ForeignKey('users.User', related_name='replacement_request', on_delete=models.CASCADE)
    company = models.ForeignKey('company.Company', related_name='company_replacement', on_delete=models.CASCADE)
    status = models.ForeignKey('company.HireStatus', on_delete=models.CASCADE)
    approved_by = models.ForeignKey('users.User', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.id)

class Advertisement(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    workplace_title = models.CharField(max_length=100, blank=True, null=True)
    job_location = models.CharField(max_length=100)
    company_name = models.CharField(max_length=255)
    description_of_job = models.TextField(null=True, blank=True)
    filter = models.CharField(max_length=150, blank=True, null=True)
    
    def __str__(self) -> str:
        return str(self.job_title)
    
    class Meta:
      abstract = False
      
class RecommendationCandidate(models.Model):
    
    candidate_name = models.CharField(max_length=255)
    candidate_skill = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return str(self.candidate_name)
    
    class Meta:
      abstract = False
    