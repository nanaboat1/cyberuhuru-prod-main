import os
import six
from io import BytesIO
from xhtml2pdf import pisa
from pdf2image import convert_from_path

# Djnago related Imports 
from django.core.files import File
from django.contrib import messages 
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Users related Imports
from users.models import Certificate


class TokenGenerator(PasswordResetTokenGenerator):
	def _make_hash_value(self, user, timestamp):
		return (
			six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
		)


class PasswordResetToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


password_reset_token = PasswordResetToken()
account_activation_token = TokenGenerator()


def check_authentication(request):
    """
    This method is used to check the authentication,
    If User Authenticated then return Requested Used object,
    If user is Not Authenticated then, it will redirect to Login page 
    """
    if (request.user.is_authenticated) and (request.user.is_candidate_user):
        user = request.user
        return user
    else:
        messages.error(request, f"Please login first")
        return None


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def convertHtmlToPdf(template, training, request):
    base_url = request.build_absolute_uri('/')[:-1] + "/static/img/cer-border2.png" 
    context = {
                'candidate_name': training.user.first_name + " " + training.user.last_name,
                'course_name': training.course.course_title,
                'completion_date': training.updated_at,
                'base_url': base_url,
            }

    pdf = render_to_pdf(template, context)
    if pdf:
        filename = f'{training.user.first_name}({training.course.course_title}).pdf'
        certificate = Certificate.objects.create(training_id=training.id)
        certificate.file.save(filename, File(BytesIO(pdf.content)))
        
        try:
            pdf_path = 'media/' + certificate.file.name
            image = convert_from_path(pdf_path)[0]
            image_path = os.getcwd() + '/media/'
            saving_path = f'uploads/{certificate.training.course.course_title}({certificate.training.user.first_name}).jpeg'  
            image.save(f'{image_path}{saving_path}', 'JPEG')
            certificate.image = saving_path
            certificate.save()
        except:
            pass