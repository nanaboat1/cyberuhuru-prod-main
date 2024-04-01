# Python Imports
from dateutil.relativedelta import relativedelta

# Django Imports 
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

# Company Related imports
from company.models import Subscription, UserSubscription

# Third-Party Imports
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received

# Create your view here. 


def paypal_process_payment (request):
    subscription_id = request.GET.get('subscription_id', None)
    subscription = get_object_or_404(Subscription, id=subscription_id)
    user_subscription = create_user_subscription(subscription, request.user)

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': str(subscription.price.amount),
        'item_name': subscription.description,
        'invoice': str(user_subscription.id),
        'currency_code': subscription.price.currency,
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
		'return_url': request.build_absolute_uri(reverse('payment_done')),
		'cancel_return': request.build_absolute_uri(reverse('payment_canceled')),
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    content = {
        'form': form,
        'title': "Annual Subscription Plan"
    }
    return render(request, "company_user/payment/process_payment.html", content)

@csrf_exempt
def payment_done(request):
	return render(request, 'company_user/payment/payment_done.html')

@csrf_exempt
def payment_canceled(request):
	return render(request, 'company_user/payment/payment_canceled.html')


def create_user_subscription(subscription, user):
    user_subscription = UserSubscription.objects.create(
      subscription=subscription, 
      user=user,
      amount=subscription.price.amount,
      currency=subscription.price.currency
    )
    return user_subscription


@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    print('ipn.payment_status', ipn.payment_status)
    if ipn.payment_status == 'Completed':
        # payment was successful
        user_subscription = get_object_or_404(UserSubscription, id=ipn.invoice)

        if user_subscription.amount == ipn.mc_gross:
            # mark the order as paid
            user_subscription.is_paid = True
            user_subscription.start_date = timezone.now()
            if user_subscription.subscription.type.upper() == 'MONTHLY':
                user_subscription.end_date = timezone.now() + relativedelta(months=1)
            elif user_subscription.subscription.type.upper() == 'YEARLY':
                user_subscription.end_date = timezone.now() + relativedelta(years=1)
            user_subscription.save()
        else:
            print("amount not matched")
    else:
        print("paymenmt status wrong")