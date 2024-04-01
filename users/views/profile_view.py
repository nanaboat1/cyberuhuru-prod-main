"""
Profile view file is used to carry profile related View classes
"""
#Python Imports
from datetime import date

# Djnago Imports
from django.views import View
from django.core import serializers  
from django.contrib import messages
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect

# User Imports
from users.utils import check_authentication
from users.models import (Experience, EducationDetails, Address, Resume)
from users.forms import (ProfileForm, ProfileImage, UploadResumeForm, ExperienceForm, EducationForm)
from users.constants import (
    HIGHEST_QUALIFICATION_CHOICES, 
    COURSE_TYPE_CHOICES, 
    PASSING_OUT_YEAR_CHOICES,
    EDUCATION_TYPE_CHOICES)

# Stats Imports
from stats.models import (CompanyAddress, Countries)

# Company Imports
from company.models import (Advertisement)

class ProfileView(View):
    '''
    Candidate Profile to Get and Post Information.
    '''
    form_class = ProfileForm
    initial = {'key': 'value'}
    template_name = 'users/profile.html'

    def get(self, request, *args, **kwargs):
        
         # Check Authentication for user
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')

        form = self.form_class(initial=self.initial)
        countries = Countries.objects.all()
        company_address = CompanyAddress.objects.all()

        context = {
            'form': form,
            'countries': countries,
            'candidate_data': user,
            'company_address': company_address,
        }
        try:
            candidate_address = Address.objects.get(user_id=user.id)
            context['candidate_address'] = candidate_address
            return render(request, self.template_name, context)
        except Address.DoesNotExist:
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            messages.error(request, f"Please login first")
            return redirect('/login/')

        res = {
            'status': False,
            'errors': {}
        }
        form = self.form_class(request.POST)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone_number')
            country = request.POST.get('country')
            state = request.POST.get('state')
            city = request.POST.get('city')

            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone_number
            user.save()

            try:
                address = Address.objects.get(user_id=user.id)
                address.country_id = country
                address.state_id = state
                address.city_id = city
                address.save()

            except Address.DoesNotExist:
                res['errors'] = f"Error occured on updating address"
                return JsonResponse(res, safe=False)

            user_data = model_to_dict(
                user, fields=['first_name', 'last_name', 'phone_number'])
            address_data = model_to_dict(address)
            res['candidate_data'] = user_data
            res['candidate_address'] = address_data
            res['status'] = True
            return JsonResponse(res, safe=False)
        else:
            res['errors'] = form.errors
            return JsonResponse(res, safe=False)


class AddProfileImageView(View):
	form_class = ProfileImage
	initial = {'key': 'value'}
	template_name = 'users/profile.html'

	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			user = request.user
		else:
			messages.error(request, f"Please login first")
			return redirect('/login/')

		context = {}
		form = self.form_class(request.POST, request.FILES)
		context['form'] = form
		if form.is_valid():
			'''
            controll your console and check if that statement appears when you click upload.
            '''
			user.profile_photo.delete(save=False) 
			user.profile_photo = request.FILES.get('profile_photo')
			user.save()
			messages.success(request, 'Profile Pic Updated!!')
			return redirect('/profile/')
		else:
			print("in else part of valid")
			

class UploadResumeView(View):
    form_class = UploadResumeForm
    initial = {'key' : 'value'}
    template_name = 'users/profile.html'
    
    def post(self, request, *args, **kwargs):
        
         # Check Authentication for user
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')
        
        form = self.form_class(request.POST, request.FILES)
        
        if form.is_valid():
            user_resume = request.FILES.get('resume')
            kwargs = {
				'resume': user_resume,
				'user_id': user.id 
			}

            try:
                resume_model_data = Resume.objects.get(user_id=user.id)
            except Exception as e:
                resume_model_data = False
                

            if resume_model_data:
                resume_model_data.resume.delete(save=False)
                resume_model_data.resume = user_resume
                resume_model_data.save()

                return redirect('/profile/')
                
            else:
                resume_model = Resume.objects.create(**kwargs)
                return redirect('/profile/')
        else:
            return redirect('/profile/')

        return redirect('/profile/')


class ShowResumeView(View):
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            messages.error(request, f"Please login first")
            return redirect('/login/')
        
        res = {}
        try:
            resume_data = Resume.objects.get(user=user)
            res['resume'] = resume_data.resume.url
            res['resume_name'] = resume_data.resume.name.rsplit('/')[1]
            return JsonResponse(res, safe=False)
        except:
            res['errors'] = f'Candidate Does not have resume'
            return JsonResponse(res,safe=False)


class EmploymentHistoryView(View):
    '''
    View Class for Experience Details Where we create GET, POST, PATCH method 
    '''
    form_class = ExperienceForm
    initial = {'key' : 'value'}
    template_name = 'users/profile.html'

    def get_queryset(self, id, user_id):
        if id is not None:
            try:
                experience = Experience.objects.get(id=id)
                return experience
            except:
                return None
        else:
            experience = Experience.objects.filter(user_id=user_id)
            return experience
            
    def get(self, request):
        '''
        Get Method To find Experience information from id or by User
        '''
        
        if request.user.is_authenticated:
            user = request.user
            id = request.GET.get('id')
        else:
            messages.error(request, f"Please login first")
            return redirect('/login/')
        
        res = {}
        experience_data = self.get_queryset(user_id=user.id, id=id) 
        try:
            res['data'] = serializers.serialize('json', experience_data)
            return JsonResponse(res, safe=False)
        except:
            res['data'] = {
                'company_name': experience_data.company_name,
                'designation': experience_data.designation,
                'currently_working': experience_data.currently_working,
                'joining_date': experience_data.joining_date,
                'end_date': experience_data.end_date,
                'skills': experience_data.skills,
                'description': experience_data.description
            }
            
            return JsonResponse(res, safe=False)


    def post(self, request):
        '''
        Post Method To add Experience details of User
        '''
        res = {
            'success' : False
        }
        experience_id = request.GET.get('id')

        if request.user.is_authenticated:
            user = request.user
        else:
            messages.error(request, f"Please login first")
            return redirect('/login/')
        
        form = self.form_class(request.POST)
        currently_working = request.POST.get('currently_working')


        if form.is_valid():
            company_name = request.POST.get('company_name')
            designation = request.POST.get('designation')
            currently_working = request.POST.get('currently_working')
            joining_date = request.POST.get('joining_date')
            end_date = request.POST.get('end_date')
            skills = request.POST.get('skills')
           
            if currently_working == 'on':
                currently_working = "Yes"
            else:
                currently_working = "No"
                
            description = request.POST.get('description')
            
            if joining_date > end_date:
                form.add_error('joining_date', f'Joining date should be less then end date')
                res['errors'] = form.errors
                return JsonResponse(res, safe=False)

        # Create a new entry of Experience of Particular Candidate
            if experience_id is None:
                experience = Experience.objects.create(
                        company_name=company_name,
                        designation=designation,
                        currently_working=currently_working,
                        joining_date=joining_date,
                        end_date=end_date,
                        skills=skills,
                        description=description,
                        user=user
                )
                res['success'] = True
                messages.success(request, f'Experience Detail added successfully')
                return JsonResponse(res, safe=False)
                
            else:  # Update entry of particular experience detail of a candidate

                experience_obj = self.get_queryset(user_id=user.id, id=experience_id)
                
                if experience_obj is not None:
                    experience_obj.company_name = company_name
                    experience_obj.designation = designation
                    experience_obj.currently_working = currently_working
                    experience_obj.joining_date = joining_date
                    experience_obj.end_date = end_date
                    experience_obj.skills = skills
                    experience_obj.description = description

                    experience_obj.save()
                    res['success'] = True
                    messages.success(request, f'Experience Detail added successfully')
                    return JsonResponse(res, safe=False)
                else:
                    return JsonResponse(res, safe=False)
            
        else:
            res['errors'] = form.errors
            print(res['errors'])
            return JsonResponse(res, safe=False)


class EducationalDetails(View):
    '''
    View Class for Education Details Where we create GET, POST, PATCH method 
    '''

    form_class = EducationForm
    initial = {'key' : 'value'}
    template_name = 'users/profile.html'
    
    def get_queryset(self, id, user_id):
        '''
        Method to find the LIST of Education if Id is not given otherwise single object return 
        '''
        if id is not None:
            try:
                education = EducationDetails.objects.get(id=id)
                return education
            except:
                return None
        else:
            education = EducationDetails.objects.filter(user_id=user_id)
            return education
      
    def get(self, request):
        '''
        Get Method to give Education Related data 
        '''
        if request.user.is_authenticated:
            user = request.user
            id = request.GET.get('id')
        else:
            messages.error(request, f"Please login first")
            return redirect('/login/')

        res = {
            'data': [],
            'errors': {},
            'highest_qualification_choices': HIGHEST_QUALIFICATION_CHOICES,
            'course_type_choices': COURSE_TYPE_CHOICES,
            'passing_out_year_choices': PASSING_OUT_YEAR_CHOICES,
            'education_type_choices': EDUCATION_TYPE_CHOICES,
        }  

        education_data = self.get_queryset(user_id=user.id, id=id) 
        try:
            res['data'] = serializers.serialize('json', education_data)
            return JsonResponse(res, safe=False)
        except:
            res['data'] = {
                'highest_qualification': education_data.highest_qualification,
                'institute': education_data.institute,
                'course_type': education_data.course_type,
                'passing_out_year': education_data.passing_out_year,
                'education_type': education_data.education_type,
            }
            return JsonResponse(res, safe=False)

    def post(self, request):
        '''
        Post Method To add/update Education details of Candidate User
        '''
        res = {
            'success': False
        }
        if request.user.is_authenticated:
            user = request.user
            education_id = request.GET.get('id')
        else:
            messages.error(request, f"Please login first")
            return redirect('/login/')

        form = self.form_class(request.POST)

        if form.is_valid():
            highest_qualification = request.POST.get('highest_qualification')
            institute = request.POST.get('institute')
            course_type = request.POST.get('course_type')
            passing_out_year = request.POST.get('passing_out_year')
            education_type = request.POST.get('education_type')

            if education_id is None:

                education = EducationDetails.objects.create(
                        highest_qualification=highest_qualification,
                        institute=institute,
                        course_type=course_type,
                        passing_out_year=passing_out_year,
                        education_type=education_type,
                        user=user
                )
                res['success'] = True
                messages.success(request, f'Education Detail added successfully')
                return JsonResponse(res, safe=False)
                
            else:  # Update entry of particular education detail of a candidate

                education_obj = self.get_queryset(user_id=user.id, id=education_id)
                
                if education_obj is not None:
                    education_obj.highest_qualification = highest_qualification
                    education_obj.institute = institute
                    education_obj.course_type = course_type
                    education_obj.passing_out_year = passing_out_year
                    education_obj.education_type = education_type

                    education_obj.save()
                    res['success'] = True
                    messages.success(request, f'Education Detail updated successfully')
                    return JsonResponse(res, safe=False)
                else:
                    return JsonResponse(res, safe=False)

        else:
            res['errors'] = form.errors
            return JsonResponse(res, safe=False)

