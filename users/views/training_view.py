"""
Training view file is used to carry Training Related View classes
"""
# Django Imports
from django.views import View
from django.core import serializers
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views.generic import View


# User Imports
from users.utils import check_authentication, render_to_pdf
from users.models import (Training, Skills, CandidateSkills, Trainingvideos)

# Stats Imports
from stats.models import (Course, CompanyAddress, CourseVideos)


class SelectSkillsView(View):
    """
    Select Skill View has two methods 'Get' and 'Post' 
    """

    initial = {'key' : 'value'}
    template_name = 'users/select_skills.html'

    def get(self, request, *args, **kwargs):
        """
        Get method is used to get the selected skills of Candidate
        """
        context = {}

        # Check Authentication for Candidate
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')

        # Flag from frontend to identification, if 'True means Show More otherwise normal'    
        click_flag = request.GET.get('click_flag',False)
        search  = request.GET.get('searched_skill', None)
        
        company_address = CompanyAddress.objects.all()
        context['company_address'] = company_address
        # get List of selected id's by candidate 
        candidate_skills_list = CandidateSkills.objects.filter(user=user).values_list('skill_id', flat=True)
    
        if click_flag:
            # This Section if Check flag is True
            skills_more = Skills.objects.exclude(
                Q(default='True') | 
                Q(id__in=candidate_skills_list)
            ).values('id', 'name')
            res = {
                'data': list(skills_more)
            }
            return JsonResponse(res, safe=False)

        elif search is not None:
            # this section is used to searched skills
            searched_data = Skills.objects.filter(name__icontains=search).values('id', 'name')
            res ={
                'skills': list(searched_data),
                'selected_skill_list': list(candidate_skills_list)
            }
            return JsonResponse(res, safe=False)

        else:
            # This Section if Check flag is False
            db_skills = Skills.objects.filter(
                Q(default='True') | Q(id__in=candidate_skills_list)
            )
            context['company_address'] = company_address
            context['db_skills'] = db_skills
            context['candidate_data'] = user
            context['candidate_skills_list'] = candidate_skills_list
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Post Method is used to add/remove Candidate skills
        """

        # Check Authentication for user
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')
        skill_id = request.GET.get('button_id', None)
        if skill_id is None:
            res = {
                    'errors': f"Skill id cannot be null on add/remove. "
            }
            return JsonResponse(res, safe=False) 
        
        db_flags={}
        
        try:
            skill = Skills.objects.get(id=skill_id)
        except Skills.DoesNotExist:
            res = {
                'errors': f"Skill Does Not Exist with ({skill_id}) id"
            }
            return JsonResponse(res, safe=False)

        try:
            user_skills = CandidateSkills.objects.filter(skill_id=skill.id).first()
            user_skills.delete()
            db_flags['del_flag'] = True
            return JsonResponse(db_flags, safe=False)
        except Exception as e:
            CandidateSkills.objects.create(skill=skill, user_id=request.user.id)            
            db_flags['create_flag'] = True
            return JsonResponse(db_flags, safe=False)


class RecommendationCoursesView(View):
    '''
    Candidate Recommendation Courses to Get Information.
    '''

    template_name = 'users/recommendation_courses.html'
    initial = {'key': 'value'}


    def get(self, request,  *args, **kwargs):
        """
        In this Method we first get Selected Skills list,
        and filter courses according to selected skills list and called 'Recommended course'
        """
        
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')

        selected_skills = CandidateSkills.objects.filter(user=user).values_list('skill__name', flat=True)
        print("selected skills --", selected_skills)
        company_address = CompanyAddress.objects.all()
        
        qs = Q()
        for skills in selected_skills:
            qs |= (Q(course_title__icontains=skills)
                | Q(course_content__icontains=skills))
        
        recommendation_courses = Course.objects.filter(qs)
        if len(recommendation_courses) == 0:
            recommendation_courses = Course.objects.all().order_by('?')[:5]
        
        train = Training.objects.filter(user=user).values_list('course_id', flat=True)

        context = {
            'candidate_data': user,
            'company_address': company_address,
            'recommendation_courses': recommendation_courses,
            'train': train
        } 

        return render(request, self.template_name,  context)


class UserTrainingView(View):
    '''
    Candidate Training to Get Information.
    '''

    template_name = 'users/user_training.html'
    initial = {'key': 'value'}

    def get(self, request,  *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            messages.error(request, f"Please login first")
            return redirect('/login/')

        company_address = CompanyAddress.objects.all()
        ongoing_training = Training.objects.filter(
                                        user=user, 
                                        is_completed=False
        ).annotate(chapter_count=Count('course__course_video'))

        completed_training = Training.objects.filter(
                                        user=user, 
                                        is_completed=True
        )
        
        context = {
            'candidate_data': user,
            'company_address': company_address,
            'ongoing_training': ongoing_training,
            'completed_training': completed_training
        }  
        return render(request, self.template_name, context)
        
    def post(self, request, *args, **kwargs):
        """
        Post Method is used to add Course in Training 
        """
        # Check Authentication for user
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')
        course_id = request.GET.get('button_id', None)

        if course_id is None:
            res = {
                    'errors': f"Skill id cannot be null on add/remove. "
            }
            return JsonResponse(res, safe=False)
        else:
            try:
                course = Course.objects.get(id=course_id)
            except:
                res = {}
                res['errors']= f'Course DoesNotExist with {course_id} id'
                return JsonResponse(res, safe=False)
            train = Training.objects.create(course=course, user= user)
            res ={
                "course_id": course_id,
                "train_flag": True
            }
            return JsonResponse(res, safe=False)


class TrainingEpisodeView(View):
    '''
    This section is used to store and get Training related videos progress
    '''

    def get(self, request):
        '''
        Get method is used to respond data  
        '''
        # Check Authentication for user
        res = {
            'success': True,
            'status_code': 200,
            'data': None
        }
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')

        course_id = request.GET.get('course_id', None)

        if course_id is not None:
            training_videos = Trainingvideos.objects.filter(training__course_id=course_id)
            res['data'] = serializers.serialize('json', training_videos)
        
        return JsonResponse(res, safe=False)
        
    def post(self, request):
        '''
        This method is used to store video progress
        '''
        # Check Authentication for user
        user = check_authentication(request)
        if user is None:
            return redirect('/login/')

        course_id = request.POST.get('course_id', None)
        episode_id = request.POST.get('episode_id', None)
        watch_progress_time = request.POST.get('current_time', None)

        training = Training.objects.filter(course_id=course_id, user=user)

        if len(training) > 0:
            training = training.first()
        else:
            res = {
                'errors': f'Training Does Not Exist with {course_id} courseId'
            }
            return JsonResponse(res, safe=False)    

        try:
            episode = CourseVideos.objects.get(id=episode_id)
        except CourseVideos.DoesNotExist:
            res = {
                'errors': f'Chapter Does Not Exist with {episode_id} id'
            }
            return JsonResponse(res, safe=False)

        training_chapter = Trainingvideos.objects.filter(training=training, episode=episode)
        if training_chapter.exists():
            training_chapter = training_chapter.first()
            if training_chapter.progress_percentage < 99:
                training_chapter.progress_percentage = int(float(watch_progress_time))
                training_chapter.save()
            res = {
                'training_chapter': model_to_dict(training_chapter),
                'success': True,
                'status_code': 200
            }
            return JsonResponse(res, safe=False)

        else:
            training_chapter = Trainingvideos.objects.create(
                                                    training=training,
                                                    episode=episode,
                                                    progress_percentage=int(float(watch_progress_time)) 
            )
            res = {
                'training_chapter': model_to_dict(training_chapter),
                'success': True,
                'status_code': 200
            }
            return JsonResponse(res, safe=False)

