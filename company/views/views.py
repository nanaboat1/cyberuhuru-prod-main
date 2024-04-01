# Python Imports
from hashlib import new
from company.utils import check_company_authentication
import json
import datetime

from collections import defaultdict

# Django Imports
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.db.models import Subquery, OuterRef, F, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# User Related Imports
from users.forms import ProfileImage
from users.models import CandidateSkills, Training, User, Address, Skills, Experience

# Company Related imports
from company.mailing import email_hiring_request
from company.forms import CompanyLogin, CompanyProfileForm
from company.models import (
    Company, Subscription, TechnolgyStack, UserSubscription,
    HireCandidate, HireStatus, ReplacementRequests,
)
from company.utils import check_company_authentication, validate_monthly_subscription, pagination

# Stats related Imports
from stats.models import Countries, Course, State, Cities, CompanyAddress

# Create your views here.
from company.models import Advertisement, RecommendationCandidate
from django.core.mail import send_mail

import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)



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
        user = check_company_authentication(request)
        if user is None:
            return redirect('/login/')

        context = {
            'form': self.form_class,
            'status': 'success',
            'error': None,
        }
        countries = Countries.objects.all()

        context['company'] = user.company_user.first()
        context['countries'] = countries

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user = check_company_authentication(request)
        if user is None:
            return redirect('/login/')

        company = user.company_user.first()
        res = {}
        if form.is_valid():

            company_name = request.POST.get('company_name')
            email_id = request.POST.get('email_id')
            phone_number = request.POST.get('phone_number')
            country = request.POST.get('country')
            city = request.POST.get('city')
            state = request.POST.get('state')
            industry = request.POST.get('industry')
            establish_at = request.POST.get('establish_at')

            user.phone_number = phone_number
            user.email_id = email_id
            user.save()

            company.company_name = company_name
            company.industry_id = industry
            company.establish_at = establish_at
            company.save()

            address = company.address
            address.country_id = country
            address.state_id = state
            address.city_id = city
            address.save()

            user_data = model_to_dict(
                user, fields=['phone_number'])
            address_data = model_to_dict(address)
            company_data = model_to_dict(company)
            res['user_data'] = user_data
            res['company_address'] = address_data
            res['company_data'] = company_data
            res['status'] = True

            return JsonResponse(res, safe=False)
        else:
            res['errors'] = form.errors
            return JsonResponse(res, safe=False)


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

        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        hire_candidate = HireCandidate.objects.filter(
            company__user_id=user.id
        )
        hiring_requests = hire_candidate.exclude(status_id=HireStatus.APPROVED)
        pending_request_count = hiring_requests.count()
        hired_candidate_count = hire_candidate.filter(
            status_id=HireStatus.APPROVED).count()

        context = {
            'hiring_requests': hiring_requests,
            'pending_request_count': pending_request_count,
            'hired_candidate_count': hired_candidate_count
        }

        return render(request, self.template_name, context)


class AnnualSubscriptionView(View):
    template_name = "company_user/company_subscription.html"

    def get(self, request):
        subscription = Subscription.objects.filter(type='yearly').first()
        context = {
            'subscription': subscription
        }
        return render(request, self.template_name, context)


class UpdateCompanyImageView(View):
    """
    This section is used to Upload and get the profile image
    """
    form_class = ProfileImage
    initial = {'key': 'value'}
    template_name = 'company/company_profile.html'

    def post(self, request, *args, **kwargs):
        """
        Post Method is used to update the profile image
        """
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        context = {
            'status': True,
            'errors': None,
            'data': None
        }
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = {}
            user.profile_photo.delete(save=False)
            user.profile_photo = request.FILES.get('profile_photo')
            user.save()

            data['profile_photo'] = user.profile_photo.url
            context['data'] = data
            return JsonResponse(context, safe=False)
        else:
            context['status'] = False
            context['errors'] = form.errors
            return JsonResponse(context, safe=False)


class MonthlySubscriptionView(View):
    """
    Get & POST methods to get data of Monthly Subscription
    """
    template_name = "company_user/hire_candidate/monthly_subscription.html"

    def get(self, request):
        """
        Get Method to get Subscription data
        """
        context = {}

        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            context['redirect'] = '/company/login'
            return JsonResponse(context, safe=True)

        is_active = validate_monthly_subscription(user)
        if is_active:
            context['redirect'] = '/company/select-technolgy-stack'
            return JsonResponse(context, safe=True)

        plan_id = request.GET.get('plan_id')
        if plan_id is not None:
            try:
                subscription = Subscription.objects.get(id=plan_id)
                context['subscription'] = {
                    'id': subscription.id,
                    'type': subscription.type,
                    'max_range': subscription.price.max_range,
                    'amount': subscription.price.amount,
                    'currency': subscription.price.currency
                }
            except:
                context["errors"] = "Plan not found with this Plan id"
            return JsonResponse(context, safe=False)
        else:
            subscription_qs = Subscription.objects.filter(type='MONTHLY').values(
                'id', 'description', 'price__currency', 'price__max_range', 'price__amount')
            context["subscriptions"] = list(subscription_qs)
            return JsonResponse(context, safe=True)


class SelectTechnologyStackView(View):
    template_name = "company_user/hire_candidate/select_technology_stack.html"

    def get(self, request):

        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        is_active = validate_monthly_subscription(user)
        if not is_active:
            return redirect('/company/view-monthlySubscription/')

        skills = Skills.objects.all()

        context = {
            'skills_set': skills
        }
        return render(request, self.template_name, context)


class TechnolgyStackView(View):
    """
    This Section is used to Get Or POST the Stack Data
    """

    def get(self, request):
        # Variable Declarations
        context = {
            'status': True,
            'errors': None,
            'data': None
        }

        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        is_active = validate_monthly_subscription(user)
        if not is_active:
            context['redirect'] = '/company/select-technolgy-stack'
            return JsonResponse(context, safe=True)

        technology_stack = TechnolgyStack.objects.filter(
            company__user_id=user.id).values('id', 'company', 'skills__id', 'skills__name')
        context['data'] = list(technology_stack)

        return JsonResponse(context, safe=True)

    def post(self, request):
        """
        Post Method is used to Update the Technolgy Stack
        """

        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        context = {
            'status': True,
            'errors': None,
            'data': None
        }
        skills_list = request.POST.getlist('skills_ids[]')

        for id in skills_list:
            try:
                technology_stack = TechnolgyStack.objects.get(
                    skills_id=id, company__user_id=user.id)
            except:
                technology_stack = TechnolgyStack.objects.create(
                    skills_id=id, company_id=user.company_user.first().id)

        technology_stack_list = TechnolgyStack.objects.filter(
            company__user_id=user.id).values('id', 'company', 'skills__id', 'skills__name')

        context['data'] = list(technology_stack_list)
        return JsonResponse(context, safe=False)


class RemoveTechnologyStack(View):
    template_name = "company/select_technology_stack.html"

    def post(self, request):
        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        context = {
            'status': True,
            'errors': None,
            'data': None
        }

        skill_id = request.POST.get('skill_id')

        try:
            technology_stack = TechnolgyStack.objects.get(
                skills_id=skill_id, company__user_id=user.id)
        except:
            context['errors'] = 'Stack Not found with this id'

        technology_stack.delete()

        context['data'] = {
            'deleted_skill_id': skill_id
        }

        return JsonResponse(context, safe=False)


class SkillsListingView(View):
    template_name = "company_user/hire_candidate/skills_listing_view.html"

    def get(self, request):

        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        is_active = validate_monthly_subscription(user)
        if not is_active:
            return redirect('/company/view-monthlySubscription/')

        technology_stack = TechnolgyStack.objects.filter(
            company__user_id=user.id)
        context = {
            'status': True,
            'errors': None,
            'technology_stack': technology_stack
        }
        return render(request, self.template_name, context)

    def post(self, request):

        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        technology_stack = TechnolgyStack.objects.filter(
            company__user_id=user.id)
        skills_json = json.loads(request.POST.get('skills'))

        for skill in skills_json:

            if skill['option[]'] != 'on':
                stack = technology_stack.filter(
                    id=int(skill['option[]'])).first()
                stack.experience = skill['experience_in_years']
                stack.no_of_candidate = skill['no_of_candidate']
                stack.is_selected = True
                stack.skills_set = skill['searched_skills']
                stack.save()

        context = {
            'status': True,
            'errors': None,
            'data': "Data updated successfully"
        }

        return JsonResponse(context, safe=False)


class CandidateResumeListingView(View):
    template_name = "company_user/hire_candidate/candidate_resume_listing.html"

    def get(self, request):
        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        is_active = validate_monthly_subscription(user)
        if not is_active:
            return redirect('/company/view-monthlySubscription/')

        # Filter data
        technology_stack = TechnolgyStack.objects.filter(
            company__user_id=user.id,
            is_selected=True
        ).values('skills', 'experience', 'skills_set')

        candidate_qs = User.objects.filter(
            is_candidate_user=True,
            is_admin=False
        )

        qs_list = []
        for stack in technology_stack:
            experience = Experience.objects.filter(
                user=OuterRef('pk')
            ).values(
                'user__pk'
            ).annotate(
                exp=Sum(F('end_date')-F('joining_date'))
            ).values('exp')

            qs = candidate_qs.annotate(
                duration=Subquery(experience)
            ).filter(
                duration__gt=datetime.timedelta(stack['experience']*365, 0, 0)
            )

            if len(qs_list) > 0:
                # combine two queryset with union operator
                qs_list[0] = qs_list[0] | qs
            else:
                qs_list.append(qs)

        output = qs_list[0]

        user_ids_list = output.values_list('id', flat=True)

        # Add Pagination Candidate user List
        page = request.GET.get('page', 1)
        # take queryset and size of page as an argument
        paginator = Paginator(output, 5)
        try:
            output = paginator.page(page)
        except PageNotAnInteger:
            output = paginator.page(1)
        except EmptyPage:
            output = paginator.page(paginator.num_pages)

        training = Training.objects.filter(user_id__in=user_ids_list)
        context = {
            'status': True,
            'errors': None,
            'candidate_qs': output,
            'user_trainings': training
        }

        return render(request, self.template_name, context)

    def post(self, request):
        """
        This method is used to add resume count for this Company user
        """

        context = {
            'status': True,
            'errors': None,

        }
        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            context['redirect'] = '/company/login'
            return JsonResponse(context, safe=True)

        is_active = validate_monthly_subscription(user)
        if not is_active:
            context['redirect'] = '/company/select-technolgy-stack'
            return JsonResponse(context, safe=True)

        subscription = UserSubscription.objects.filter(
            user_id=user.id,
            is_paid=True,
            subscription__type='MONTHLY'

        ).latest('created_at')

        if subscription:
            subscription.resumes_count += 1
            subscription.save()
            context['message'] = "Resume Viewed Successfully"

        return JsonResponse(context, safe=False)


class HireCandidateView(View):
    """
    This class to create Post method to create hire candidate,
    Get Method to get the hired candidate.

    """

    def post(self, request):
        """
        This Method is to create a hire candidate 
        """

        # Variables declartion
        context = {
            'status': True,
            'errors': None,

        }
        users_list = []

        # Check Authentication For company user
        user = check_company_authentication(request)
        if user is None:
            context['redirect'] = '/company/login'
            return JsonResponse(context, safe=True)

        candidate__ids_list = request.POST.getlist('candidate_ids_list[]')

        if len(candidate__ids_list) <= 0:
            context['status'] = False
            context['errors'] = 'Please select atleast one candidate to hire..'
            return JsonResponse(context, safe=False)

        hired_candidate = HireCandidate.objects.filter(
            candidate_id__in=candidate__ids_list
        ).values_list('id', flat=True)

        for candidate_id in candidate__ids_list:
            user_dict = {}
            created_candidate = HireCandidate.objects.create(
                candidate_id=candidate_id,
                company_id=user.company_user.first().id,
                status_id=HireStatus.PENDING
            )
            user_dict['username'] = created_candidate.candidate.first_name + \
                created_candidate.candidate.last_name
            user_dict['email'] = created_candidate.candidate.email_id
            users_list.append(user_dict)

        context['message'] = 'Thank you for your submission. We are reviewing your request and will get back to you ASAP.'

        if context['errors'] is None:
            email_hiring_request(users_list, company=user.company_user.first())

        return JsonResponse(context, safe=False)


class PreviousRequestView(View):
    template_name = "company_user/hire_candidate/previous_request.html"

    def get(self, request):
        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        hiring_requests = HireCandidate.objects.filter(
            company__user_id=user.id
        ).exclude(status_id=HireStatus.APPROVED)
        context = {
            'hiring_requests': hiring_requests
        }
        return render(request, self.template_name, context)


class HiredCandidateView(View):
    """
    This class used to get Hired Candidate list with Get method
    """
    template_name = "company_user/hire_candidate/hired_candidate.html"

    def get(self, request):
        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        # Variable declaration
        context = {
            'status': True,
            'errors': None,
            'search': ''
        }

        search = request.GET.get('search')
        hired_candidate = HireCandidate.objects.filter(
            company__user_id=user.id,
            status_id=HireStatus.APPROVED
        )

        if search is not None:
            hired_candidate = hired_candidate.filter(
                candidate__first_name__icontains=search
            )
            context['search'] = search

        # Add Pagination Candidate user List
        page = request.GET.get('page', 1)
        # take queryset and size of page as an argument
        paginator = Paginator(hired_candidate, 2)
        try:
            hired_candidate = paginator.page(page)
        except PageNotAnInteger:
            hired_candidate = paginator.page(1)
        except EmptyPage:
            hired_candidate = paginator.page(paginator.num_pages)

        context['hired_candidates'] = hired_candidate

        return render(request, self.template_name, context)


class ReplacementRequestView(View):
    """
    This class is used to create and get Replacement request
    """
    template_name = "company_user/hire_candidate/replacement_requests.html"

    def get(self, request):

        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        # Variable Declaration
        context = {
            'search': ""
        }

        replacement_requests = ReplacementRequests.objects.filter(
            company__user_id=user.id
        )
        page = request.GET.get('page', 1)
        search = request.GET.get('search')

        if search is not None:
            replacement_requests = replacement_requests.filter(
                candidate__first_name__icontains=search
            )
            context['search'] = search
        paginated_queryset = pagination(
            queryset=replacement_requests, page=page, pagesize=5)

        context['replacement_request'] = paginated_queryset

        return render(request, self.template_name, context)

    def post(self, request):
        """
        Post method is used to replacement request
        """
        # Check Authentication For user
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        # Variable Declaration
        context = {
            'status': True,
            'errors': None,
            'message': None
        }
        candidate_id = request.POST.get('candidate_id')

        if candidate_id is not None:
            try:
                qs = ReplacementRequests.objects.filter(
                    company__user_id=user.id,
                    candidate_id=candidate_id
                )
                if len(qs) == 0:
                    ReplacementRequests.objects.create(
                        company_id=user.company_user.first().id,
                        candidate_id=candidate_id,
                        status_id=HireStatus.PENDING
                    )
                    context = {
                        'status': True,
                        'errors': None,
                        'message': f'Replacement request successfully created'
                    }
                    return JsonResponse(context, safe=False)
                else:
                    context['status'] = False
                    context[
                        'errors'] = f'Replacement request is already submitted for candidate({qs.first().candidate.first_name})'
                    return JsonResponse(context, safe=False)
            except Exception as e:
                context['status'] = False
                context['errors'] = f'Error({e})'
                return JsonResponse(context, safe=False)
        else:
            context['status'] = False
            context['errors'] = f'Please Select Candidate first'
            return JsonResponse(context, safe=False)


def AdvertisementView(request):
    if request.method == 'POST':
        # -----------  Check Authentication For user  --------------
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        comp_id = Company.objects.get(user_id=request.user.id)
        job_title = request.POST.get('job_title')
        workplace_title = request.POST.get('workplace_title')
        job_location = request.POST.get('job_location')
        company_name = request.POST.get('company_name')
        description_of_job = request.POST.get('description_of_job')
        filter = request.POST.get('Filter')

        contact = Advertisement(job_title=job_title, workplace_title=workplace_title, job_location=job_location,
                                company_name=company_name, description_of_job=description_of_job, company=comp_id, filter=filter)
        contact.save()

    return render(request, 'company_user/hire_candidate/advertisement.html')

def Send_request(request):
    send_mail(
        'Hiring request {{Candidate Name}}',
        '{{user}} Company has choosen {{Candidate Name }} Candidate.',
        env('EMAIL_HOST_USER'),
        [env('ADMIN_EMAIL')],
        fail_silently=False,
    )
    return redirect('/company/recommendation_candidate/')

class RecommendationCandidateView(View):
    '''
    Recommendation of candidate to the Company.
    '''

    template_name = 'company_user/hire_candidate/recommended_candidate.html'
    initial = {'key': 'value'}

    def get(self, request,  *args, **kwargs):
        """
        In this Method we first get Selected Skills list,
        and filter courses according to selected skills list and called 'Recommended course'
        """

        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')

        UserSkill = Training.objects.all()
        top = UserSkill.values_list('user_id', 'course_id__course_title')

        diction = {}
        for x, y in top:
            diction.setdefault(x, []).append(y.lower())
        # print("Diction Result  -==-=-=-=-=-=-=>>>>>", diction)

        required_skills = Advertisement.objects.values_list(
            'company_id', 'job_title')
        # print("required Skills ---", required_skills)
        my_dict = {}
        for i, j in required_skills:
            my_dict.setdefault(i, []).append(j.lower())

        # print('____________________________________________________')
        recommended_candidate_skills = []
        candidate_list = defaultdict(list)
        for data in my_dict:
            # print("Advertisement Company ID", data)
            for key in diction:
                for val in diction[key]:
                    # print("val", val)
                    recommended_candidate_skills.append(val)
                    for di in my_dict[data]:
                        if val == di:
                            # print('value of Key ------>>>>', key)
                            candidate_list[data].append(key)
        
        
        recommended_candidate_data = []
        recommended_candidate_email = []
        recommended_candidate_phone = []
        recommended_candidate_skill = []

        for company_id in candidate_list.keys():
            cmp_id = Company.objects.get(id=company_id).user_id
            if user.id == cmp_id:
                for abc in candidate_list[company_id]:
                    cand_name = User.objects.get(id=abc).first_name
                    cand_mail_address = User.objects.get(id=abc).email_id
                    cand_phone_number = User.objects.get(id=abc).phone_number
                    cand_skill = Training.objects.filter(user_id=abc).values_list('course_id__course_title')
                    
                    recommended_candidate_data.append(cand_name)
                    recommended_candidate_email.append(cand_mail_address)
                    recommended_candidate_phone.append(cand_phone_number)
                    recommended_candidate_skill.append(cand_skill)

        recommended_candidate_data = list(dict.fromkeys(recommended_candidate_data))
        new_list = [list(vallll) for vallll in recommended_candidate_skill]

        # Save data to the RecommendationCandidate model
        for candidate_name, skills in zip(recommended_candidate_data, new_list):
            render_data = RecommendationCandidate(candidate_name=candidate_name, candidate_skill=skills, company_name=user)
            render_data.save()
        print('recommended_candidate_data', recommended_candidate_data)
        print("new_list", new_list)
        
        context = {
            'candidate_data': recommended_candidate_data,
            'candidate_email': recommended_candidate_email,
            'candidate_phome': recommended_candidate_phone,
            'candidate_skills': new_list,
        }

        return render(request, self.template_name, context)


def HiringCandidateView(request):
    if request.method == 'GET':
        print('-----------  Check Authentication For user  --------------')
        user = check_company_authentication(request)
        if user is None:
            return redirect('/company/login/')
        
        print("--------------+++++++++-----------------------")
        RecommendedCandidate = RecommendationCandidate.objects.all()
        print("recommended_candidate_data", RecommendedCandidate)
        # recommended_candidate_data = RecommendationCandidateView.request.get('candidate_data')
        # print("recommended_candidate_data", recommended_candidate_data)
        # if request.method == 'POST':
     
  
        # candidate_id =RecommendationCandidateView
    
        # print("recommended_candidate_data", recommended_candidate_data)
        # recommended_candidate_skill = RecommendationCandidateView.recommended_candidate_skill
        # print("recommended_candidate_skill", recommended_candidate_skill)
        
        
        # render_data = RecommendationCandidate(candidate_name=RecommendationCandidateView,candidate_skill = recommended_candidate_skill[:1], company_name = user )
        # render_data.save()
    if request.method == 'POST':
        print("Method is GET")
    return render(request, 'company_user/hire_candidate/recommended_candidate.html')