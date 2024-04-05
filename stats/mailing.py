import six
import smtplib

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from stats.models import Messages


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(timestamp) + six.text_type(user.is_active)
            # six.text_type(user.id) +
        )


class PasswordResetToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(timestamp) +
                six.text_type(user.is_active)
            # six.text_type(user.id) +
        )


password_reset_token = PasswordResetToken()
account_activation_token = TokenGenerator()


def send_verification_email(user, request):
    email_subject = 'Activate Your Account'
    to_email = user.email

    if user.is_candidate_user:
        activation_url = request.build_absolute_uri(reverse('activate')) + '?token='
    elif user.is_company_user:
        activation_url = request.build_absolute_uri(reverse('company_user_activation')) + '?token='

    print("token", activation_url)
    token = account_activation_token.make_token(user)
    user.token = token
    user.save()

    try:
        html_content = render_to_string('emails/account_activation.html', {
            'user': user,
            'activation_url': activation_url + str(token),
            'token': token,
        })
        print("token url", html_content['activation_url'])
    except Exception as e:
        print("Error rendering email content:", e)
        return

    email = EmailMultiAlternatives(email_subject, body=html_content, to=[to_email])
    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)


def email_user_verification_link(user, request):
    email_subject = 'Activate Your Account'
    email = user.email_id
    # uid = urlsafe_base64_encode(force_bytes(user.id))
    token = account_activation_token.make_token(user)
    user.token = token
    user.save()

    if user.is_candidate_user:
        reverse_url = 'activate'
    elif user.is_company_user:
        reverse_url = 'company_user_activation'

    try:
        html_content = render_to_string('emails/account_activation.html', {
            'user': user,
            'activation_url': request.build_absolute_uri(reverse(reverse_url)) + '?token=' + str(token),
            'token': token,
        })
    except Exception as e:
        pass
    to_email = email
    email = EmailMultiAlternatives(email_subject, html_content, to=[to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()


def email_user_forgot_password(user, request):
    email_subject = 'Reset Password'
    email = user.email_id
    token = password_reset_token.make_token(user)
    user.token = token
    user.save()

    if user.is_candidate_user:
        html = 'emails/reset_password.html'
        reverse_url = 'reset_password'
        user_context = user
    elif user.is_company_user:
        html = 'emails/company_reset_password.html'
        reverse_url = 'company_reset_password'
        user_context = user.company_user.first().company_name
    elif user.is_admin:
        html = 'emails/admin_reset_email.html'
        reverse_url = 'change_admin_password'
        user_context = user
        print("Inside elif of admin user")

    html_content = render_to_string(html, {
        'user': user_context,
        'reset_url': request.build_absolute_uri(reverse(reverse_url)) + '?token=' + str(token),
        'token': token,
    })
    to_email = email
    email = EmailMultiAlternatives(email_subject, html_content, to=[to_email])
    email.attach_alternative(html_content, "text/html")
    print("before send mail")
    email.send()
    print("after send mail")


def email_send_message(email_id):
    message = Messages.objects.all()
    for msz in message:
        subject = msz.subject
        text = msz.text

    email_subject = subject
    html_content = text
    # html_content = render_to_string(text)
    to_email = email_id
    # to_email = 'suman.saurav@sourcesoftsolutions.com'
    email = EmailMultiAlternatives(email_subject, html_content, to=[to_email])
    email.attach_alternative(html_content, "text/html")
# email.send()
