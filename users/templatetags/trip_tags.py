# Python related imports
import datetime
from pathlib import Path
from ast import Subscript

# Django related Imports
from django.contrib import admin
from django import template
from django.db.models import Sum
from django.utils import timezone

# User related Imports
from users.models import User

# Comapny Related imports
from company.models import Company, UserSubscription

register = template.Library()


@register.inclusion_tag('admin/custom_menu.html')
def custom_app_list(request):
    # Get all models and add them to the context apps variable.
    app_list = admin.site.get_app_list(request)
    print('app_list: ', app_list)
    return {'app_list': app_list}


@register.simple_tag
def dashboard_list(request):
    # Get all models and add them to the context apps variable.
    user_qs = User.objects.filter(is_active=True)

    candidate_user = user_qs.filter(is_candidate_user=True)
    company_user = user_qs.filter(is_company_user=True)
    user_subscription = UserSubscription.objects.filter(
        user_id__in= company_user.values_list('id', flat=True),
        is_paid=True
    )
    subscribed_company = user_subscription.filter(
        subscription__type='YEARLY',
        end_date__gte=timezone.now()
    ).values('user').distinct()

    subscription_revenue = user_subscription.filter(
        subscription__type='YEARLY'
    ).aggregate(Sum('amount'))
    
    hiring_revenue = user_subscription.filter(
        subscription__type='MONTHLY'
    ).aggregate(Sum('amount'))

    if subscription_revenue['amount__sum'] == None:
        subscription_amount = 0
    else:
        subscription_amount = subscription_revenue['amount__sum']

    if hiring_revenue['amount__sum'] == None:
        hiring_amount = 0
    else:
        hiring_amount = hiring_revenue['amount__sum']
        
    context={
        'total_candidate_user': candidate_user.count(),
        'total_company_user': company_user.count(),
        'total_subscribed_company': subscribed_company.count(),
        'subscription_revenue': subscription_amount,
        'hiring_revenue': hiring_amount,
    }

    return context
