# Django Imports 
from django.views import View
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse 
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect

# User Related Imports 
from users.models import User, Address

# Company Related imports
from company.models import Company
from company.forms import (
  CompanyRegistrationForm, CompanyLogin, CompanyForgotPassword,CompanyResetPasswordForm, ChangePasswordForm
)
from company.utils import check_company_authentication

# Stats related Imports
from stats.models import Countries, Industry, State, Cities, CompanyAddress
from stats.mailing import email_user_forgot_password

# Class based view wite here 

class CompanyRegistrationView(View):
    form_class = CompanyRegistrationForm
    initial = {'key': 'value'}
    template_name = 'company_user/company_register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        countries = Countries.objects.all()
        company_address = CompanyAddress.objects.all()
        context = {
            'countries': countries,
            'company_address': company_address,
            'form': form
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        '''
        Post method to register new company User, get data from form
        '''
        context = {
            'status': False,
			'message': 'Invalid Request',
			'data': {},
			'errors': {}
        }
        form = self.form_class(request.POST)

        if form.is_valid():
            company_name = request.POST.get('company_name')
            email_id = request.POST.get('email_id')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            industry_id = request.POST.get('industry')
            country_id = request.POST.get('country')
            state_id = request.POST.get('state')
            city_id = request.POST.get('city')
            establish_at = request.POST.get('establish_at')

            # create Dictionary for User create
            kwargs = {
                "compnay_name": company_name,
                "email_id": email_id,
                "phone_number": phone_number,
                "is_active": False,
                "is_company_user": True
            }

            try:
                country = Countries.objects.get(id=country_id)
            except Countries.DoesNotExist:
                form.add_error('country', f'Country Does Not Exist')
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)
                
            try:
                state = State.objects.get(id=state_id)
            except Exception as e:
                form.add_error('state', f'State Does Not Exist')
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)
                
            try:
                city = Cities.objects.get(id=city_id)
            except Exception as e:
                form.add_error('city', f'City Does Not Exist')
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)
                
            try:
                industry = Industry.objects.get(id=industry_id)
            except Industry.DoesNotExist:
                form.add_error('industry', f'Industry Does Not Exist')
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)
                
            # create user
            user = User.objects.create_user(**kwargs)

            try:
                address_val = Address.objects.create(
                    address=address,
                    country=country,
                    state=state,
                    city=city,
                    user=user
                )
                print("address val", address_val)
                company = Company.objects.create(
                    company_name=company_name,
                    industry=industry,
                    establish_at=establish_at,
                    user=user,
                    address=address_val
                )
                print("company", company)
            except Exception as e:
                messages.error(
                    request, f"Some thing went wrong")
                form.add_error(None, str(e))
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)

            context['status'] = True
            context['message'] = 'To confirm your email address, tap the link in the email we have sent to!'
            context['data'] = {'email': user.email_id}
            context['errors'] = {}
            return JsonResponse(context, safe=False)
            
        else:
            print("in else means errors", form.errors)
            context['errors'] = form.errors
            return JsonResponse(context, safe=False)
            

class CompanyLoginView(View):
    form_class = CompanyLogin
    template_name = 'company_user/company_login.html'
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):

        form = self.form_class(initial=self.initial)
        company_address = CompanyAddress.objects.all()
        context = {
            'form': form,
            "company_address": company_address
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        '''
        Company Login Post method to Authenticate Company User
        '''
        form = self.form_class(request.POST)

        context = {'form': form}

        if form.is_valid():
            email_id = request.POST.get('email_id')
            password = request.POST.get('password')

            # User Authentication
            user = authenticate(request, email_id=email_id, password=password)

            if (user is not None) and (user.company_user.exists()):
                login(request, user)
                if user.company_user.first().is_subscribed():
                    return redirect("/company/profile/")
                else:
                    return redirect("/company/profile/")
            elif user is None:
                messages.error(request, f"Sorry wrong Username/Password..")
                return render(request, self.template_name, context)
            else:
                messages.error(request, f"Sorry you are not registered with us as a Company")
                return render(request, self.template_name, context)
        else:
            messages.error(request, form.errors)
            return render(request, self.template_name, context)


class CompanyForgotPasswordView(View):
    form_class = CompanyForgotPassword
    template_name = 'company_user/company_forgot_password.html'
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):
        company_address = CompanyAddress.objects.all()
        form = self.form_class(initial=self.initial)
        context = {
            'form': form,
            "company_address": company_address
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        template_name = 'users/forgot_password.html'
        context = {}
        user = request.user
 
        if form.is_valid():
            email_id = request.POST.get('email_id')
            email_exists = User.objects.filter(email_id__iexact=email_id).exists()

            if email_exists:
                user = User.objects.get(email_id=email_id)
                if user.is_company_user == True:
                    email_user_forgot_password(user, request)
                    context['status'] = True
                    context['email_id'] = email_id
                    return JsonResponse(context, safe=False)
                else:
                    print("Please activate your account first")
                    return JsonResponse(context, safe=False)
            else:
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)
        else:
            context['errors'] = form.errors
            return JsonResponse(context, safe=False)

class LogoutView(View):

    initial = {'key': 'value'}
    template_name = 'stats/index.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')

  
class CompanyResetPasswordView(View):
    form_class = CompanyResetPasswordForm
    
    initial = {'key': 'value'}
    template_name = 'company_user/company_reset_password.html'

    def get(self, request):
        form = self.form_class(initial=self.initial)
      
        context = {
            'form': form
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        context = {
            'form': form
        }
        token = request.GET.get('token')
        user = User.objects.get(token=token)
        if form.is_valid():
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:
                user.set_password(confirm_password)
                user.save()              
                return redirect('/company/login')
            else:
                messages.error(request, f"Password & confirm Password doesn't match")
                return render(request, self.template_name)   
        else:
            context['errors'] = form.errors
            return render(request, self.template_name, context)


class CompanyUserActivationView(View):
    def get(self, request):

        try:
            print("Inside get of candidate activation view")
            print(request)
            token = request.GET.get('token')
            user = User.objects.get(token=token)
        except Exception as e:
            print("Exception1: ",e)

        try:    
            if user.is_active:
                print("User is already activated")
                return redirect('/company/login/')
            else:
                print("Activated the user")
                user.is_active=True
                user.save()
                messages.success(request, 'Account activated successfully')
                return redirect('/company/login/')
        except Exception as e:
            print("Exception2: ", e)

        messages.error(request, 'Something went wrong please register again!!')
        return redirect('/company/register/')


class ChangePasswordView(View):
    """
    This section is used to Change the password
    """
    def __init__(self):
        self.form_class = ChangePasswordForm
        self.template = 'company_user/company_profile.html'
        self.initial = {'key': 'value'}

    def post(self, request, *args, **kwargs):
        """
        Get old password and new password, 
        if old password is correct then update the password with new
        """

        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        context = {
            'status': True,
            'data': None,
            'errors': None
        }
        form = self.form_class(request.POST)

        # Form validation
        if form.is_valid():
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            is_correct = user.check_password(old_password)
            
            if is_correct:
                data = {}
                user.set_password(new_password)
                user.save()
                data['message'] = f'Password changed successfully!'
                context['data'] = data
                return JsonResponse(context, safe=False)
            else:
                context['status'] = False
                form.add_error('old_password', f'Password is incorrect ')
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)
        else:
            context['status'] = False
            context['errors'] = form.errors
            return JsonResponse(context, safe=False)

