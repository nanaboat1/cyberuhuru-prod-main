# Django Imports 
from django.urls import reverse
# from django.conf.urls import url
from django.urls import re_path

from django.shortcuts import redirect
from django.utils.html import format_html
from django.contrib import messages, admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# User related Imports
from users.forms import UserChangeForm
from users.utils import password_reset_token
from users.views.admin_view import UserDetailView
from users.models import (
        Training, User, Address, EducationDetails, Experience, 
        Resume, Agreement, Test, TestAnswer, Certificate, Skills
)

# Stats related imports
from stats.mailing import email_send_message

# Register your Class here.


# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     form = UserChangeForm
#     list_display = ('email_id', 'is_active')
#     list_filter = ('is_active', 'is_admin', 'is_prime',)
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Edit', {'fields': ('first_name', 'last_name', 'email_id', 'profile_photo', 'uid')}),
#     )
#     search_fields = ('email_id', 'phone_number')
#     ordering = ('-pk',)
#     filter_horizontal = ()


class CandidateUser(User):
    class Meta:
        proxy = True
        verbose_name = _("Candidate user")
        verbose_name_plural = _("Candidate user")


@admin.register(CandidateUser)
class CustomerUserAdmin(admin.ModelAdmin):    
    list_per_page = 5
    list_display_links = ['candidate_user']
    list_display = (
        'candidate_user', 
        'email_id', 
        'phone_number',
        'address', 
        'account_actions', 
        'details',

    )
    search_fields = ['email_id', 'phone_number']
    fieldsets = (
        ('Edit', {'fields': ('first_name', 'last_name', 'is_active', 'profile_photo')}),
    )
    
    def get_queryset(self, request):
        qs = super(CustomerUserAdmin, self).get_queryset(request)
        return qs.filter(is_active=True, is_candidate_user=True)
    
    def process_edit(self, request, user_id, *args, **kwargs):
        return redirect('/admin/users/candidateuser/' + user_id + '/change/')
    
    def process_delete(self, request, user_id, *args, **kwargs):
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        messages.success(request, 'User successfully delete.')
        return redirect(request.META['HTTP_REFERER'])

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<user_id>.+)/edit/$',
                self.admin_site.admin_view(self.process_edit),
                name='candidate-edit',
            ),
            re_path(
                r'^(?P<user_id>.+)/delete/$',
                self.admin_site.admin_view(self.process_delete),
                name='candidate-delete',
            ),
            re_path(
                r'^(?P<user_id>.+)/detail/$',
                self.admin_site.admin_view(UserDetailView.as_view()),
                name='user-detail',
            ),
        ]
        return custom_urls + urls

    @admin.display(ordering='id', description='Address')
    def address(self, obj):
        return format_html(
            '<a href="{}" title="Address list" alt="Address List">{}</a>'.format(
                reverse(
                    "admin:users_address_changelist",
                ) + 
                '?user_id=' + str(obj.id),
                '<i class="fa fa-external-link"></i>'
            )
        )

    @admin.display(ordering='id', description='Actions')
    def account_actions(self, obj):
        return format_html(
            '<a href="{}" title="Candidate Update" alt="Candidate Update">{}</a> '.format(
                reverse('admin:candidate-edit', args=[obj.pk]), 
                '<i class="fa fa-edit" style="color:blue"></i>'
            ) + 
            '<a href="{}" title="Candidate Delete" alt="Candidate Delete">{}</a>'.format(
                reverse('admin:candidate-delete', args=[obj.pk]),
                '<i class="fa fa-trash-o" style="color:red"></i>'
            )
        )
    account_actions.allow_tags = True
     
    @admin.display(ordering='email_id', description='Details')
    def details(self, obj):
        return format_html(
            '<a href="{}" title="Candidate Detail" alt="Candidate Detail">{}</a> '.format(
                reverse('admin:user-detail', args=[obj.pk]),
                '<i class="fa fa-info-circle" style="color:black"></i>'
            )
        )
    details.allow_tags = True

    @admin.display(ordering='first_name', description='Full Name')
    def candidate_user(self, obj):
        if obj.first_name and obj.last_name:
            full_name = str(obj.first_name) + " " + str(obj.last_name)
        else:
            full_name = str(obj.username)
        return full_name


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'city', 'state', 'country')
    list_per_page = 10


@admin.register(EducationDetails)
class EducationDetailAdmin(admin.ModelAdmin):
    list_display = ('highest_qualification', 'institute', 'course_type', 'passing_out_year', 'education_type')
    list_per_page = 10


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = (
        'company_name', 
        'designation', 
        'currently_working', 
        'joining_date', 
        'end_date', 
        'skills', 
        'description'
    )
    list_per_page = 10


@admin.register(Certificate)
class CertificateeAdmin(admin.ModelAdmin):
    list_display = (
        'show_image',
        'course_name',
    )
    list_per_page = 10

    @admin.display(ordering='id', description='Certificate')
    def show_image(self, obj):
        return format_html(
            '<img name="certificate" src="{}" width=100 height=100>'.format(
                obj.image.url
            )
        )

    @admin.display(ordering='id', description='Course Name')
    def course_name(self, obj):
        return obj.training.course.course_title


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        'resume', 
    )
    list_per_page = 10


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'default', 
    )
    list_per_page = 10


admin.site.unregister(Group)

admin.site.register(Agreement)
admin.site.register(Test)
admin.site.register(TestAnswer)
admin.site.register(Training)