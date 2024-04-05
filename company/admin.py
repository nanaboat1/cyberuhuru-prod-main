
# Django imports
from django.utils.html import format_html
# from django.conf.urls import url
from django.urls import re_path
from django.urls import reverse
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib import messages
# from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _

# User App related imports
from users.models import User

# Comapny App related imports
from .models import Company, HireCandidate, Price, Subscription, TechnolgyStack, UserSubscription, HireCandidate
from .mailing import email_company_user_credentials

# Register your models here.


class CompanyUser(Company):
	class Meta:
		proxy = True
		verbose_name = _("Company User")
		verbose_name_plural = _("Company User")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
	list_display = (
		'company_name', 
		'email', 
		'phone_number', 
		'company_address', 
		'establish_at',
		'subscription_left',
		'details', 
		'account_activate',
	)
	search_fields = ('user__email_id', 'user__phone_number', 'company_name')
	list_per_page = 10

	@admin.display(ordering='id', description='Email ID')
	def email(self, obj):
		print("self", obj.user)
		return obj.user.email_id
	
	@admin.display(ordering='id', description='Phone Number')
	def phone_number(self, obj):
		print("self", obj.user)
		return obj.user.phone_number

	@admin.display(ordering='id', description='Address')
	def company_address(self, obj):
		return format_html(
            '<a href="{}" title="Address list" alt="Address List">{}</a>'.format(
                reverse(
                    "admin:users_address_changelist",
                ) + 
                '?user_id=' + str(obj.user.id),
                '<i class="fa fa-external-link"></i>'
            )
        )

	@admin.display(ordering='id', description='Details')
	def details(self, obj):
		return format_html(
            '<a href="{}" title="Company Detail" alt="Company Detail">{}</a> '.format(
                reverse('admin:company_hirecandidate_changelist'
				) + 
				'?company_id=' + str(obj.id),
                '<i class="fa fa-info-circle" style="color:black"></i>'
            )
        )
	details.allow_tags = True

	@admin.display(ordering='id', description='Subscription Duration')
	def subscription_left(self, obj):
		if (obj.subscription_days_remaining()) == 0:
			return 'Expired'
		else:
			return str(obj.subscription_days_remaining()) + ' days'

	def process_account_activate(self, request, obj, *args, **kwargs):
		company_user = Company.objects.get(company_name=obj)
		user = company_user.user
		print("Savings company to user")
		user.save()

		if user.is_company_user == True and user.is_active == False:
			password = User.objects.make_random_password()
			user.set_password(password)
			print(f"Company Credentials email {user.email_id}  password {password}")
			user.is_active = True
			user.save()
			email_company_user_credentials(user, password)
			messages.success(request, 'Mail Send successfully.')
			print("Mail Send successfully.")
		else:
			messages.warning(request, "User's account is already activated ")
			print("User's account is already activated")
		return redirect(request.META['HTTP_REFERER'])

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			re_path(
				r'^(?P<obj>.+)/company_activate/$',
				self.admin_site.admin_view(self.process_account_activate),
				name='account-company_activate'
			)
		]
		return custom_urls + urls

	@admin.display(ordering='id', description='Activate')
	def account_activate(self, obj):
		if obj.user.is_active:
			button_icon = '<i class="fa fa-toggle-on"></i>'
		else:
			button_icon = '<i class="fa fa-toggle-off"></i>'
		return format_html(
			'<a title="Account Activate" alt="Account Activate" href="{}">{}</a>'.format(
				reverse('admin:account-company_activate', args=[obj]),
				button_icon
			)
		)

@admin.register(HireCandidate)
class HiredCandidateAdmin(admin.ModelAdmin):
	list_display = (
		'candidate_name',
		'company_name',
		'contract_duration',
  		'designation',
		'experience',
		'status_name',
	)
	list_per_page = 10

	@admin.display(ordering='id', description='Company Name')
	def company_name(self, obj):
		if obj.company.company_name:
			full_name = str(obj.company.company_name) 
		else:
			full_name = "--"
		return full_name
	
	@admin.display(ordering='id', description='Candidate Name')
	def candidate_name(self, obj):
		if obj.candidate.first_name:
			full_name = str(obj.candidate.first_name) + ' '  + str(obj.candidate.last_name) 
		else:
			full_name = obj.candidate.username
		return full_name
	
	@admin.display(ordering='id', description='Designation')
	def designation(self, obj):
		return obj.candidate.current_designation()

	@admin.display(ordering='id', description='Experience')
	def experience(self, obj):
		return obj.candidate.experience_in_years()
	

	@admin.display(ordering='id', description='Status')
	def status_name(self, obj):
		if obj.status:
			status = str(obj.status.name)
		else:
			status = "--"
		return status

	@admin.display(ordering='id', description='Contract Duration')
	def contract_duration(self, obj):
		return "--"
	
	@admin.display(ordering='id', description='No. Of Candidate')
	def no_of_candidates(self, obj):
		technology_stack = TechnolgyStack.objects.filter(company=obj.company).first()
		return format_html(
			'<a title="No. of Candidate" alt="No. of candidate" href="{}">{}</a>'.format(
				reverse('admin:company_technolgystack_changelist'),
				technology_stack.no_of_candidate
			)
		)


@admin.register(TechnolgyStack)
class TechnologyStackAdmin(admin.ModelAdmin):
	list_display = (
		'no_of_candidate',
		'experience',
		'skills_set', 
	)
	list_per_page = 10


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
		'description',
		'price',
		'type', 
	)
    list_per_page = 10


admin.site.register(CompanyUser, CompanyAdmin)
admin.site.register(Price)
admin.site.register(UserSubscription)