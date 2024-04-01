"""
View File carry All Authentication and candidate related View classes
"""
# Python Imports
from logging import raiseExceptions
import time
import json
from datetime import timedelta

# Djnago Imports
from django.views import View
from django.db.models import Q, F
from django.contrib import messages
from django.core import serializers
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator

# User Imports
from users.utils import check_authentication, convertHtmlToPdf
from users.models import (Training, User, Address, Agreement, TestAnswer, Test as UserTest, Certificate)
from users.forms import (SignUpForm, LoginForm, UserForgotPassword, 
                            ResetPasswordForm, ChangePasswordForm, SignedAgreementForm)

# Stats Imports
from stats.models import (AnswerChoices, CompanyAddress, Countries, Course, Questions, State, Cities, Test)
from stats.mailing import email_user_verification_link, email_user_forgot_password

# company Imports 
from company.utils import check_company_authentication
from company.models import Advertisement

class RegistrationView(View):
    form_class = SignUpForm
    initial = {'key': 'value'}
    template_name = 'users/registration.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        countries = Countries.objects.all()
        company_address = CompanyAddress.objects.all()

        context = {
            'countries': countries,
            'form': form,
            "company_address": company_address

        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        res = {
            'status': False,
            'message': 'Invalid Request',
            'data': {},
            'errors': {}
        }

        form = self.form_class(request.POST)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email_id = request.POST.get('email_id')
            password = request.POST.get('password')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            country = request.POST.get('country')
            state = request.POST.get('state')
            city = request.POST.get('city')

            kwargs = {
                "first_name": first_name,
                "last_name": last_name,
                "email_id": email_id,
                "password": password,
                "phone_number": phone_number,
                "is_active": False,
                "is_candidate_user": True
            }
            user = User.objects.create_user(**kwargs)

            try:
                country = Countries.objects.get(id=country)
            except Countries.DoesNotExist:
                form.add_error('country', f'Sorry Country Id Does Not Exists')
                res['errors'] = form.errors
                return JsonResponse(res, safe=False)

            try:
                state = State.objects.get(id=state)
            except State.DoesNotExist:
                form.add_error('state', f'Sorry State Id Does Not Exists')
                res['errors'] = form.errors
                return JsonResponse(res, safe=False)

            try:
                city = Cities.objects.get(id=city)
            except Cities.DoesNotExist:
                form.add_error('city', f'Sorry City Id Does Not Exists')
                res['errors'] = form.errors
                return JsonResponse(res, safe=False)

            try:
                Address.objects.create(
                    address=address,
                    country=country,
                    state=state,
                    city=city,
                    user=user
                )
                current_site = request.build_absolute_uri('/')[:-1]

                email_user_verification_link(user, request)
                user.save()

                res['status'] = True
                res['message'] = 'To confirm your email address, tap the link in the email we have sent to!'
                res['data'] = {'email': email_id}
                res['errors'] = {}
                return JsonResponse(res, safe=False)
                
            except Exception as e:
                res['message'] = ''
                res['data'] = {}
                res['errors'] = {}
                return JsonResponse(res, safe=False)
        else:
            res['errors'] = form.errors
            return JsonResponse(res, safe=False)


class LoginView(View):
    form_class = LoginForm
    template_name = 'users/login.html'
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):
        
        form = self.form_class(initial=self.initial)
        company_address = CompanyAddress.objects.all()
        context = {
            'form': form,
            'company_address': company_address
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        '''
        Post method to Authenticate candidate user
        '''
        form = self.form_class(request.POST)

        context = {'form': form}

        # Form Validation
        if form.is_valid():
            email_id = request.POST.get('email_id')
            password = request.POST.get('password')

            # User authentication
            user = authenticate(request, email_id=email_id, password=password)
            print("User", user)

            # check User is not anonymous and Candidate
            if (user is not None) and (user.is_candidate_user == True):
                login(request, user)
                return redirect('/profile/')
            elif user is None:
                form.add_error(None, f'Sorry wrong Username/Password..')
                context['errors'] = form.errors
                return render(request, self.template_name, context)
            else:
                form.add_error(
                    None, f'Sorry you are not registered with us as a candidate')
                context['errors'] = form.errors
                return render(request, self.template_name, context)
        else:
            context['errors'] = form.errors
            return render(request, self.template_name, context)


class ForgetPassword(View):
    form_class = UserForgotPassword
    initial = {'key': 'value'}
    template_name = 'users/forgot_password.html'

    def get(self, request, *args, **kwargs):
        
        form = self.form_class(initial=self.initial)
        company_address = CompanyAddress.objects.all()
        context = {
            'form': form,
            'company_address': company_address
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        context = {}
        user = request.user
 
        if form.is_valid():
            email_id = request.POST.get('email_id')
            email_exists = User.objects.filter(email_id__iexact=email_id).exists()

            if email_exists:
                user = User.objects.get(email_id=email_id)
                if user.is_candidate_user == True:
                    # email_user_forgot_password(user, request)
                    context['status'] = True
                    context['email_id'] = email_id
                    return JsonResponse(context, safe=False)
                else:
                    context['error_message'] = f'Entered emailId is not registered with us as a Candidate, please enter valid emailId.'
                    return JsonResponse(context, safe=False)
            else:
                context['errors'] = form.errors
                return JsonResponse(context, safe=False)
        else:
            context['errors'] = form.errors
            return JsonResponse(context, safe=False)


class ResetPasswordView(View):
    form_class = ResetPasswordForm
    initial = {'key': 'value'}
    template_name = 'users/reset_password.html'

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
                return redirect('/login')  
        else:
            context['errors'] = form.errors
            return render(request, self.template_name, context)
            #return render(request, self.template_name)

        return render(request, self.template_name)


class ChangeUserPasswordView(View):
    form_class = ChangePasswordForm
    template_name = 'users/change_password.html'
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            messages.error(request, f"Please login first")
            time.sleep(1)
            return redirect('/login/')
            
        form = self.form_class(initial=self.initial)
        company_address = CompanyAddress.objects.all()
        context = {
			'form': form,
			'company_address' : company_address,
            'candidate_data': user
		}
        
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        company_address = CompanyAddress.objects.all()
        user = request.user
        context = {'company_address': company_address, 'candidate_data' :user}
        res = {
            'status': False,
            'errors': {}
        }
        if form.is_valid():

            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            try:
                check_pass = user.check_password(old_password)

                if check_pass:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, f"Password Changed Successfully!!")
                    res['status'] = True
                    return JsonResponse(res, safe=False) #redirect('/login')
                else:
                    form.add_error('old_password', f'Entered old password is wrong!!')
                    res['errors'] = form.errors
                    return JsonResponse(res, safe=False)
            except Exception as e:
                print("Exception in changing user password", e)

        else:         
            res['errors'] = form.errors
            return JsonResponse(res, safe=False)

 
class AgreementView(View):
    '''
    Candidate Agreement to Get and Post Information.
    '''
    template_name = 'users/agreement.html'
    initial = {'key': 'value'}
    form_class = SignedAgreementForm
    
    def get_queryset(self, user):
        """
        This method is used to get objects through Authenticated user,
        if Agreement is not there then return error message 
        """

        try:
            agreement = Agreement.objects.get(user=user)
            return agreement, None
        except Agreement.DoesNotExist:
            return None, f'Agreement does not exist with this Candidate'

    def get(self, request,  *args, **kwargs):
        """
        This Method is used to Get Uploaded Agreement documents
        """
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')
        
        company_address = CompanyAddress.objects.all()
        context = {
            'candidate_data' : user,
            'company_address': company_address
        }
        
        
        agreement, error = self.get_queryset(user)
        if error is not None:
            context['errors'] = error
            return render(request, self.template_name, context)
    
        context['agreement'] = agreement
        return render(request, self.template_name, context)
    

    def post(self, request, *args, **kwargs):
        """
        This Method is used to upload the Signed Document 
        In agreement using Form 
        """

        context = {}
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')

        agreement, error = self.get_queryset(user)
        if error is not None:
            context['errors'] = error
            return JsonResponse(context, safe=False)

        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            signed_doc = request.FILES['upload_file']
            if agreement.signed_document.name:
                agreement.signed_document.delete(save=False)

            agreement.signed_document = signed_doc
            agreement.save()

            context = {
                'agreement': agreement
            }
            messages.success(request, f'File Uploaded successfully')
            return render(request, self.template_name, context)
        else:
            context['errors'] =form.errors
            return render(request, self.template_name, context)


class UserCertificateView(View):
    '''
    Candidate Certificate to Get Information.
    '''

    template_name = 'users/user_certificate.html'
    initial = {'key': 'value'}


    def get(self, request,  *args, **kwargs):

         # Check Authentication for user
        user = check_authentication(request)

        if user is None and (check_company_authentication(request) is None):
            return redirect('/login/')
        company_address = CompanyAddress.objects.all()
        
        candidate_id = request.GET.get('candidate_id')
        
        if candidate_id is not None:
            certificates = Certificate.objects.filter(
                training__user=candidate_id
            ).values(
                course_title= F('training__course__course_title'),
                certificate_image = F('image')
            )
            context = {
                'certificates': list(certificates)
            }
            return JsonResponse(context, safe=False)
        else:
            certificates = Certificate.objects.filter(training__user=user)
        context = {
            'candidate_data': user,
            'certificates': certificates,
            'company_address': company_address
        }  

        return render(request, self.template_name, context)


class CandidateActivationView(View):
    
    def get(self, request, *args, **kwargs):

        try:
            token = request.GET.get('token')
            user = User.objects.get(token=token)
        except Exception as e:
            pass
        try:    
            if user.is_active:
                return redirect('/login/')
            else:
                user.is_active=True
                user.save()
                messages.success(request, 'Account activated successfully')
                return redirect('/login/')
        except Exception as e:
            pass
        messages.error(request, 'Something went wrong please register again!!')
        return redirect('/register/')


class TestView(View):

    template_name = 'users/test/test.html'

    def check_test_answer_exists(self, question,user,user_test):

        test_answer = TestAnswer.objects.filter(
                                            question_id=question.id, 
                                            user=user,
                                            user_test=user_test
        )
        
        return test_answer

    def get(self, request, *args, **kwargs):
        
        user = check_authentication(request)
        
        if user is None:
            return redirect('/login/')
        course_id = request.GET.get('course_id')
        # Get Test object from databse for a particular test id
        test = Test.objects.get(course_id=course_id)

        # Get Questions of that particular test from database
        question = Questions.objects.filter(test_id=test.id)

        paginator = Paginator(question, 1)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_number)

        context = {
            'question': question,
            'page_obj': page_obj,
            'duration' : test.duration,
            'test_id': test.id,
            'course_id': course_id, 
        }
        
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        
        user = check_authentication(request)

        if user is None:
            return redirect('/login/')
        
        question_id = request.GET.get('question_id', None)
        selected_answer = request.GET.get('selected_value', None)
        
        if question_id is not None:
            try:
                question = Questions.objects.get(id=question_id)
                correct_answer = question.answer
                test_id = question.test.id
            except:
                pass
        
        course_id = question.test.course.id
        user_training = Training.objects.filter(user_id=user.id, course_id=course_id).first()

        user_test = UserTest.objects.filter(
                                        training__user_id=user.id, 
                                        training_id=user_training.id, 
                                        is_submitted=False
        )
        
        if len(user_test) == 0:
            user_test = UserTest.objects.create(training_id = user_training.id)
            user_test.test.add(test_id)
        else:
            user_test = user_test.first()

        test_answer = self.check_test_answer_exists(question, user, user_test)

        if selected_answer is not None:
            if selected_answer.lower() == correct_answer.lower():
                
                if not test_answer.exists():
                    test_answer = TestAnswer.objects.create(
                                question_id=question.id,
                                answer=selected_answer,
                                user_test_id=user_test.id,
                                user_id=user.id
                    )
            else:
                if test_answer.exists():
                        test_answer.delete()
        else:
            if test_answer.exists():
                test_answer.delete()    
        
        return render(request, self.template_name)


class CalculateResult(View):

    def post(self, request, *args, **kwargs):

        user = check_authentication(request)

        if user is None:
            return redirect('/login/')

        _time = request.GET.get('time')
        duration = request.GET.get('duration')
        test_id = request.GET.get('test_id')
        modal_dict={}

        # It is mandatory please don't remove it until new functionality
        time.sleep(2)

        if _time and duration:

            _time = _time.split(":")
            duration = duration.split(":")
            test_completed = timedelta(hours=int(_time[0]), minutes=int(_time[1]), seconds=int(_time[2]))
            test_duration = timedelta(hours=int(duration[0]), minutes=int(duration[1]), seconds=int(duration[2]))
            time_taken = test_duration-test_completed
            
            test_obj = Test.objects.filter(id=test_id).first()
            
            user_test = UserTest.objects.filter(training__user=user, test__id=test_obj.id).latest('created_at')
            test_answer_count = user_test.UserTest.count()
            
            candidate_percentage = (test_answer_count/test_obj.no_of_questions)*100
            
            user_test.is_submitted = True
            user_test.percentage_attained = candidate_percentage
            user_test.time_taken = str(time_taken)
            user_test.save()
            value_dict = {
                'test_answer_count': test_answer_count,
                'no_of_questions': test_obj.no_of_questions,
                'candidate_percentage': str(candidate_percentage)[:5],
                'time_taken': str(time_taken),
                'test_name': test_obj.name.title()
            }
            
            if  candidate_percentage >= test_obj.pass_percentage:
                training = user_test.training
                value_dict['is_passed'] = 'PASS'
                training.is_completed = True
                training.save()
                if not hasattr(training, 'training_certificate'):
                    try:
                        convertHtmlToPdf('users/test/certificate_pdf.html', training, request)
                    except Exception as e:
                        raiseExceptions("convertHtmlToPDF",e)
            else:
                value_dict['is_passed'] = 'FAIL'

            modal_dict['data'] = value_dict

        return JsonResponse(modal_dict, safe=False)


class TestInstructionView(View):
    '''
    This section is used to show the Instruction page of Test
    '''
    template_name = 'users/test/test_instructions.html'

    def get(self, request, course_id):
        '''
        This method is used to give Test related instructions
        '''
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')

        company_address = CompanyAddress.objects.all()
        res = {
            'errors': None,
            'data': None,
            'status': 200,
            'candidate_data': user,
            'company_address': company_address
        }
        try:
            test_qs = Test.objects.get(course_id=course_id)
            print('test_qs: ---->>', test_qs)
            res['data'] = test_qs
            return render(request, self.template_name, res)
        except Test.DoesNotExist:
            messages.error(request, f'Test Does not exist with course id({course_id})')
            return redirect('/candidate/training/')


class CompanyAdvertisement(View):    
    def get(self, request):
        advert = Advertisement.objects.filter(job_title= "SSS")
        print("Advert", advert.values())
        return render(request, 'users/advertisement.html')
        
# def CompanyAdvertisement(request):
    
#     if request.method == 'GET':
#         advert = Advertisement.objects.all()
#         print("Advert", advert)
#     return render(request, 'users/advertisement.html')
