# Django Imports
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# User related imports
from users.models import User


def email_company_user_credentials(user, password=None):
  email_subject = 'Account Credentials!'
  email = user.email_id
  print("email", email)
  html_content = render_to_string('emails/company_user_credentials.html', {
		'user': user,
		'email': email,
		'password': password,
	})
  print("html_content", html_content)
  to_email = email
  email = EmailMultiAlternatives(email_subject, html_content, to=[to_email])
  email.attach_alternative(html_content, "text/html")
  email.send()
  print("after email.send")


def email_hiring_request(users_list, company):
  admin_email = settings.ADMIN_EMAIL
  email_subject = 'Hiring Requests!'
  
  # Content and Html page for Email
  html_content = render_to_string('emails/company_hiring_request.html', {
		'users_list': users_list,
    'company': company
	})
  
  email = EmailMultiAlternatives(email_subject, html_content, to=admin_email)
  email.attach_alternative(html_content, "text/html")
  email.send()
  