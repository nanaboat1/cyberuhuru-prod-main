import time

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.contrib import messages

from users.models import User, Address, Experience

from stats.models import Countries, Industry, State, Cities, CompanyAddress

from company.models import Company

from company.forms import (CompanyRegistrationForm, CompanyLogin, CompanyForgotPassword,
                           CompanyProfileForm, ChangePasswordForm, HireCandidateForms, 
                           CompanyResetPasswordForm)

from users.constants import (INDUSTRY_TYPE_CHOICES, ESTABLISH_YEAR_CHOICES)

from stats.mailing import email_user_verification_link, email_user_forgot_password

# Create your views here.


class CompanyRegistrationView(View):
    form_class = CompanyRegistrationForm
    initial = {'key': 'value'}
    template_name = 'company_user/company_register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        countries = Countries.objects.all()
        company_address = CompanyAddress.objects.all()
        context = {
            # 'company_contact': company_contact,
            # 'home_page': home_page,
            # 'home_name': menu[0],
            # 'about_us_name': menu[1],
            # 'faqs_name': menu[2],
            # 'contact_us_name': menu[3],
            # 'pricing_name': menu[4],
            # 'become_a_vendor_name': menu[5]
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
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email_id = request.POST.get('email_id')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            industry_id = request.POST.get('industry')
            password = request.POST.get('password')
            # confirm_password = request.POST.get('confirm_password')
            country_id = request.POST.get('country')
            state_id = request.POST.get('state')
            city_id = request.POST.get('city')
            establish_at = request.POST.get('establish_at')

            # create Dictionary for User create
            kwargs = {
                "compnay_name": company_name,
                "first_name": first_name,
                "last_name": last_name,
                "email_id": email_id,
                "password": password,
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
            current_site = request.build_absolute_uri('/')[:-1]
            email_user_verification_link(user, request)

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
        company_address = CompanyAddress.objects.all()
        form = self.form_class(initial=self.initial)
        context = {
            'form': form,
            "company_address": company_address
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        '''
        Compamy Login Post method to Authenticate Company User
        '''
        form = self.form_class(request.POST)

        context = {'form': form}
        if form.is_valid():
            email_id = request.POST.get('email_id')
            password = request.POST.get('password')
            user = authenticate(request, email_id=email_id, password=password)

            if (user is not None) and (user.company_user.exists()):
                print("user authenticated")
                login(request, user)
                # messages.success(f'Welcome {user.first_name} in CyberUhuru')
                return redirect("/company/profile/")
            elif user is None:
                form.add_error(None, f'Sorry wrong Username/Password..')
                context['errors'] = form.errors
                return render(request, self.template_name, context)
            else:
                form.add_error(
                    None, f'Sorry you are not registered with us as a Company')
                context['errors'] = form.errors
                return render(request, self.template_name, context)
        else:
            context['errors'] = form.errors
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
            print("company forgot password form is valid")

            if email_exists:
                user = User.objects.get(email_id=email_id)
                if user.is_company_user is True:
                    email_user_forgot_password(user, request)
                    context['status'] = True
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
        
        context['errors'] = form.errors
        return render(request, self.template_name, context)


class CompanyProfileView(View):
    '''
    Company Profile View class is a View based class.
    It is used to used Get and Post Company Profile Info.
    '''
    form_class = CompanyProfileForm
    template_name = 'company_user/company_profile.html'

    def get(self, request, *args, **kwargs):
        '''
        Get method to get Company profile data 
        '''
        print("------------in get Method")
        context = {}
        if request.user.is_authenticated:
            print("in if")
            user = request.user

            try:
                add = Address.objects.get(user_id=user.id)
            except Exception as e:
                context['errors'] = str(e)
                return render(request, self.template_name, context)

            try:
                company = Company.objects.get(user_id=user.id)
            except Exception as e:
                context['errors'] = str(e)
                return render(request, self.template_name, context)
            try:
                country = Countries.objects.get(id=add.country)
                state = State.objects.get(id=add.state)
                city = Cities.objects.get(id=add.city)
            except Exception as e:
                context['errors'] = str(e)
                return render(request, self.template_name, context)

            office_address = CompanyAddress.objects.all().first()
            industry_choices = INDUSTRY_TYPE_CHOICES
            establish_year_choices = ESTABLISH_YEAR_CHOICES

            context['company_user'] = user
            context['company'] = company
            context['country'] = country
            context['company_state'] = state
            context['city'] = city
            context['form'] = self.form_class
            context['establish_year_choices'] = establish_year_choices
            context['industry_choices'] = industry_choices
            context['office_address'] = office_address
            context['countries_choices'] = Countries.objects.all()
            context['states_choices'] = State.objects.filter(
                country_id=country.id)
            context['cities_choices'] = Cities.objects.filter(
                state_id=state.id)
            print("----context", context)
            return render(request, self.template_name, context)
        else:
            context['errors'] = f'Sorry You are not authenticates yet, Please login first..'
            # return render(request, self.template_name, context)
            return redirect('/company/login/')


    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        print("inside post of company profile")
        user_id = request.user.id
        print(user_id)

        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email_id = request.POST.get('email_id')
            phone_number = request.POST.get('phone_number')
            profile_photo = request.POST.get('profile_photo')
            company_name = request.POST.get('company_name')
            country = request.POST.get('country')
            city = request.POST.get('city')
            state = request.POST.get('state')
            industry = request.POST.get('industry')
            establish_year = request.POST.get('establish_year')
            print("company profile form is valid")

            try:
                current_user = User.objects.get(id=user_id)
            except Exception as e:
                print("Exception in current_user", e)

            try:
                add = Address.objects.get(user_id=user_id)
            except Exception as e:
                print("Exception in add", e)

            try:
                current_company_user = Company.objects.get(user_id=user_id)
            except Exception as e:
                print("Exception in current_company_user", e)

            if first_name:
                current_user.first_name = first_name

            if last_name:
                current_user.last_name = last_name

            if email_id:
                current_user.email_id = email_id

            if phone_number:
                current_user.phone_number = phone_number

            if company_name:
                current_company_user.company_name = company_name

            if industry:
                current_company_user.industry = industry

            if establish_year:
                current_company_user.establish_year = establish_year

            if country and state and city:

                country_name = Countries.objects.filter(id=country).values()
                state_name = State.objects.filter(id=state).values()
                city_name = Cities.objects.filter(id=city).values()

                country_name = country_name[0].get('country')
                state_name = state_name[0].get('state')
                city_name = city_name[0].get('city')

                add.country = country_name
                add.state = state_name
                add.city = city_name

            current_user.save()
            current_company_user.save()
            add.save()
            return redirect("/company/login/")

        return render(request, self.template_name)


class ChangePasswordView(View):
    form_class = ChangePasswordForm
    template = 'company_user/company_profile.html'
    initial = {'key': 'value'}

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            messages.error(request, f"Please login first")
            return redirect('/login/')
        
        form = self.form_class(request.POST)
        if form.is_valid():
            user = request.user
            context = {'user': user}

            print('user+++++++++++++==', user)
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            password_check = user.check_password(old_password)
            print('password_check+++++++++++', password_check)
            try:

                if password_check:
                    print('new_password++++++++', new_password)
                    user.set_password(new_password)
                    user.save()
                    # messages.success(request, 'Password updated successfully! Please login again!!')

                    return redirect("/company/login/")

                else:
                    messages.error(
                        request, "Entered old password is incorrect")

            except Exception as e:
                print('Exception in password check', e)

            return render(request, self.template, context)

        messages.error(
            request, "New Password and Confirm New Password should be same")
        return render(request, self.template)


# class HireCandidateView(View):
# 	form_class = HireCandidateForms


class SubscriptionView(View):
    form_class = CompanyLogin
    template_name = 'company_user/company_subscription.html'
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):
        company_address = CompanyAddress.objects.all()
        form = self.form_class(initial=self.initial)
        context = {
            'form': form,
            "company_address": company_address
        }

        return render(request, self.template_name, context)


class CompanyDashboardView(View):

    initial = {'key': 'value'}
    template_name = 'company_user/company_dashboard.html'

    def get(self, request, *args, **kwargs):
        company_address = CompanyAddress.objects.all()
        context = {
            "company_address": company_address
        }
        return render(request, self.template_name, context)


class LogoutView(View):

    initial = {'key': 'value'}
    template_name = 'stats/index.html'

    def get(self, request, *args, **kwargs):
        # company_address = CompanyAddress.objects.all()
        # context = {
        # 	"company_address": company_address
        # }

        logout(request)
        return redirect('/')
        # return render(request, self.template_name)


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
        token = request.GET.get('token')
        user = User.objects.get(token=token)
        if form.is_valid():
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:
                user.set_password(confirm_password)
                print(user.is_active)
                user.save()              
                return redirect('/company/login')  
        else:
            return render(request, self.template_name)

        return render(request, self.template_name)


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