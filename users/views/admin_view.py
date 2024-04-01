#File Imports
from users.forms import ResetPasswordForm
from users.forms import AdminPasswordResetRequestForm

#Django Imports
from django.views import View
from django.urls import reverse
from django.contrib import admin
from django.http import JsonResponse
from django.utils.html import format_html
from django.shortcuts import render, redirect 

# stats related imports 
from stats.mailing import email_user_forgot_password

# user app related imports
from users.models import User, Certificate


# write your code here 
class AdminForgotPassword(View):
        template_name = "admin/forgot_password.html"
        initial = {'key': 'value'}
        success_url = '/admin/login'
        form_class = AdminPasswordResetRequestForm

        def get(self, request):
            form = self.form_class(initial=self.initial)
            context = {
            'form': form,
            }
            return render(request, self.template_name, context)

        def post(self, request):
            form = self.form_class(request.POST)
            context = {}
            # user = request.user
            
            if form.is_valid():
                email_id = request.POST.get('email_id')
                email_exists = User.objects.filter(email_id__iexact=email_id).exists()
                if email_exists:
                    user = User.objects.get(email_id=email_id)
                    if user.is_admin == True:
                        email_user_forgot_password(user, request)
                        context['status'] = True
                        context['email_id'] = email_id
                        return JsonResponse(context, safe=False)
                    else:
                        context['status'] = False
                        context['error_message'] = f'Email-ID is not registered with us as Admin, Please enter valid Email-ID.'
                        return JsonResponse(context, safe=False)
                else:
                    context['status'] = False
                    context['errors_message'] =  f'Email-ID is not registered with us as Admin, Please enter valid Email-ID.'
                    return JsonResponse(context, safe=False)
            else:
                context['status'] = False
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)


class AdminResetPasswordView(View):
    form_class = ResetPasswordForm
    initial = {'key': 'value'}
    template_name = 'admin/reset_password.html'

    def get(self, request):
                
        form = self.form_class(initial=self.initial)
        token = request.GET.get('token')
        user = User.objects.get(token=token)
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        token = request.GET.get('token')
        user = User.objects.get(token=token)
        context = {'form':form}

        if form.is_valid():
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
        
                user.set_password(confirm_password)
                user.is_active = True
                user.save()
                return redirect('/admin')  
        else:
            context['errors'] = form.errors
            return render(request, self.template_name, context)

        return render(request, self.template_name)


class MyAdminSite(admin.AdminSite):
            pass

mysite = MyAdminSite()


class UserDetailView(View):

  def get(self, request, user_id):
    """[summary]

    Args:
        request ([type]): [description]
        user_id ([type]): [description]
    """    

    # Variable declaration
    link_data = []
    data = {}

    try:
        candidate = User.objects.get(id=user_id)
    except:
        pass

    # Educational Related append
    if candidate.educational.exists():
        data['link'] =  format_html(
            '<a href="{}" title="Education Listing" alt="Education Listing">{}</a>'.format(
                reverse(
                    "admin:users_educationdetails_changelist"
                ) + 
                '?user_id=' + str(user_id),
                '<i class="fa fa-info-circle" style="color:black"></i>'
            )
        )
    data['name'] = f'Educational details'
    data['count'] = candidate.educational.count()
    link_data.append(data)
    data = {}
    
    # Experience Related append 
    if candidate.experience.exists():
        data['link'] =  format_html(
            '<a href="{}" title="Education Listing" alt="Education Listing">{}</a>'.format(
                reverse(
                    "admin:users_experience_changelist"
                ) + 
                '?user_id=' + str(user_id),
                '<i class="fa fa-info-circle" style="color:black"></i>'
            )
        )
    data['name'] = f'Experience details' 
    data['count'] = candidate.experience.count()
    link_data.append(data)
    data = {}

    # Certificates related append
    if candidate.candidate_training.exists():
        data['link'] =  format_html(
            '<a href="{}" title="Education Listing" alt="Education Listing">{}</a>'.format(
                reverse(
                    "admin:users_certificate_changelist"
                ) + 
                '?training_user_id=' + str(user_id),
                '<i class="fa fa-info-circle" style="color:black"></i>'
            )
        )
    data['name'] = f'Certificates details' 
    data['count'] = Certificate.objects.filter(training__user_id=candidate.id).count()
    link_data.append(data)
    data = {}

    # Resume Related append
    if candidate.resume.exists():
        data['link'] =  format_html(
            '<a href="{}" title="Education Listing" alt="Education Listing">{}</a>'.format(
                reverse(
                    "admin:users_resume_changelist"
                ) + 
                '?user_id=' + str(user_id),
                '<i class="fa fa-info-circle" style="color:black"></i>'
            )
        )
    data['name'] = f'Resumes details' 
    data['count'] = candidate.resume.count()
    link_data.append(data)
    data = {}

    # Response
    context = {
        'user': request.user,
        'site_header': mysite.site_header,
        'has_permission': mysite.has_permission(request), 
        'site_url': mysite.site_url,
        'data': link_data
    }
    return render(request, 'admin/users/detail.html', context)