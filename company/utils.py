
import datetime

# Djnago related Imports 
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def check_company_authentication(request):
    """
    This method is used to check the authentication,
    If User Authenticated then return Requested User object,
    If user is Not Authenticated then, it will redirect to Login page 
    """
    if (request.user.is_authenticated) and (request.user.is_company_user):
        user = request.user
        return user
    else:
        messages.error(request, f"Please login first")
        return None


def validate_monthly_subscription(user):
    """
    This Method is used to check validity of Monthly Subscription
    If subscription expired return False else return True 
    """
    
    subscription = user.user_subscriptions.filter(
        is_paid=True,
        subscription__type='MONTHLY', 
        end_date__gte=timezone.now()
    )
    if len(subscription) > 0:
        calculated_data = subscription.aggregate(
            total_resumes_viewed=Sum('resumes_count'),
            total_resumes_limit=Sum('resumes_limit')
        )
        if calculated_data['total_resumes_limit'] > calculated_data['total_resumes_viewed']:
            return True
        else:
            return False
    else:
        return False


def pagination(queryset, page, pagesize):
    paginator = Paginator(queryset, pagesize) # take queryset and size of page as an argument
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    
    return queryset