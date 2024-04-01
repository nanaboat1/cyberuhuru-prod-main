import json
# import cv2
import os
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, request
from django.shortcuts import render, redirect
from django.views import View

from stats.models import (Countries, Course, State, Cities, CourseVideos,  About, CompanyAddress,
	Home, HomeVideos, VistorContact, Welcome, Industry)

from stats.serializers import IndustrySerializer, StateSerializer, CitySerializer


class IndexView(View):
	template_name = 'stats/index.html'

	def get(self, request,  *args, **kwargs): 
		home = Home.objects.all()
		welcome = Welcome.objects.all()
		company_address = CompanyAddress.objects.all()
		home_videos = HomeVideos.objects.all().first()
		course = Course.objects.all()
		
		context = {
				"home": home, 
				"welcome": welcome, 
				"company_address": company_address, 
				"home_videos": home_videos, 
				"courses": course,
				"template_name": self.template_name,
		}

		return render(request, self.template_name, context)


class AboutView(View):
	template_name = "stats/about.html"

	def get(self, request, *args, **kwargs):
		about = About.objects.all()
		company_address = CompanyAddress.objects.all()
		context = {
			"about": about, 
			"company_address": company_address 
		}
		return render(request, self.template_name, context)

class BlogView(View):
    template_name = "stats/blog.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class CourseView(View):
	template_name = "stats/course-list.html"
	
	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			user = request.user
		else:
			messages.error(request, f"Please login first")
			return redirect('/login/')
		
		company_address = CompanyAddress.objects.all()
		course = Course.objects.all()
		
		context = {
			"candidate_data": user,
			"company_address": company_address, 
			"course": course
		}
		return render(request, self.template_name, context)


class CourseDetailView(View):
	template_name = "stats/course-detail.html"

	def get(self, request, course_id, *args, **kwargs):
		if request.user.is_authenticated:
			user = request.user
		else:
			messages.error(request, f"Please login first")
			return redirect('/login/')
		
		company_address = CompanyAddress.objects.all()
		course= Course.objects.get(id=course_id)
		
		 #  To Show Course Intro Info 
		course_created_at = course.created_at
		course_title = course.course_title
		course_content = course.course_content
		course_vid = course.video_url

		course_chapters = CourseVideos.objects.filter(courses_id=course)		

		context = {
			"candidate_data": user, 
			"company_address": company_address, 
			"course_chapters": course_chapters,
			"course_title": course_title,
			"course_content": course_content,
			"course_vid" :course_vid,
			"course_created_at": course_created_at,
			"course_id": course.id,
			"course_thumbnail": course.thumbnail
		}
		return render(request, self.template_name, context)

		
class VisitorContactView(View):
	template_name ="stats/contact.html"

	def get(self, request, *args, **kwargs):
		company_address = CompanyAddress.objects.all()
		context = {
			"company_address": company_address 
		}
		
		return render(request, self.template_name, context)

	def post(self,request, *args, **kwargs):
		company_address = CompanyAddress.objects.all()
		
		first_name = request.POST.get("first_name")
		last_name = request.POST.get("last_name")
		phone_number = request.POST.get("phone_number")
		email_id = request.POST.get("email_id")
		message = request.POST.get("message")

		contact = VistorContact(first_name=first_name, last_name=last_name, 
					email_id=email_id, phone_number=phone_number, message=message)

		context = {
			"company_address": company_address 
		}
		
		contact.save()
		messages.success(request, 'You message has been sent!')
		
		return render(request, self.template_name, context)
	


class StatesView(View):	
	def post(self, request, *args, **kwargs):
		res = {
			'status': False,
			'data': {},
		}
		country_id = request.POST.get('country_id')
		selected_state_id = request.POST.get('state_id')

		states = State.objects.filter(country_id=country_id)
		states_ids = states.values_list('id', flat=True)
		serializer = StateSerializer(states, many=True)

		if(selected_state_id not in states_ids):
			statedata = '<option selected disabled>State*</option>'
		else:
			statedata = '<option disabled>State*</option>'
		res['status'] = True
		for data in serializer.data:
			state_id = data['id']
			state_name = data['state']
			if str(state_id) == selected_state_id: 
				statedata += '<option selected value="'+ str(state_id)+'">'+ str(state_name)+'</option>'
			else:
				statedata += '<option value="'+ str(state_id)+'">'+ str(state_name)+'</option>'
			
		res['data'] = statedata

		return JsonResponse(res, safe=False)
		

class CitiesView(View):
	def post(self, request, *args, **kwargs):
		res = {
			'status': False,
			'data': {},
		}
		state_id = request.POST.get('state_id')
		selected_city_id = request.POST.get('city_id')
	
		cities = Cities.objects.filter(state_id=state_id)
		cities_ids = cities.values_list('id',flat=True)
		serializer = CitySerializer(cities, many=True)

		if(selected_city_id not in cities_ids):
			citydata = '<option selected disabled>City*</option>'
		else:
			citydata = '<option disabled>City*</option>'
		res['status'] = True
		
		for data in serializer.data:
			city_id = data['id']
			city_name = data['city']
			if str(city_id) == selected_city_id: 
				citydata += '<option selected value="'+ str(city_id)+'">'+ str(city_name)+'</option>'
			else:
				citydata += '<option value="'+ str(city_id)+'">'+ str(city_name)+'</option>'
		res['data'] = citydata

		return JsonResponse(res, safe=False)


class IndustryView(View):
	'''
	View Class to create get post methods for Industry
	'''
	def get_query(self):
		return Industry.objects.all()

	def get(self, request, *args, **kwargs):
		'''
		Get method for Industry
		'''	
		res = {
			'status': True,
			'data': {},
		}
		selected_industry_id = request.GET.get('industry_id')
		
		industry = Industry.objects.all()
		industries_id = industry.values_list('id', flat=True)
		serializer = IndustrySerializer(industry, many=True)

		if(selected_industry_id not in industries_id):
			industry_data = '<option selected disabled>Industry*</option>'
		else:
			industry_data = '<option disabled>City*</option>'

		for data in serializer.data:
			industry_id = data['id']
			industry_name = data['name']
			if str(industry_id) == selected_industry_id:
				industry_data += '<option selected value="'+ str(industry_id)+'">'+ str(industry_name)+'</option>'
			else:
				industry_data += '<option value="'+ str(industry_id)+'">'+ str(industry_name)+'</option>'
		res['data'] = industry_data
		return JsonResponse(res, safe=False)


class CertificateView(View):
	template_name = "stats/certificate.html"

	def get(self, request, *args, **kwargs):
		company_address = CompanyAddress.objects.all()
		context = {
			"company_address": company_address 
		}
		return render(request, self.template_name, context)


class SearchView(View):
	template_name = "stats/search_list.html"

	def get(self, request, *args, **kwargs):
		company_address = CompanyAddress.objects.all()
		context = {
			"company_address": company_address
		}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):

		company_address = CompanyAddress.objects.all()
		
		searched = request.POST['searched']
		course_List = Course.objects.filter(course_title__icontains = searched)
		context = {
			"company_address": company_address,
			"searched": searched, 
			"course_List": course_List
		}
		return render(request, self.template_name, context)


class CompanyAddressView(View):
	'''
	This section is used to show the company address
	'''

	def get(self, request):
			company_address = CompanyAddress.objects.all().first()
			print('company_address', company_address)
			context = {
					'company_address': company_address.company_address,
					'contact_number': company_address.contact_number,
					'email_address': company_address.email_address,
			}
			return JsonResponse(context, safe=False)



			