# Django Related Imports
from django import views
from django.contrib import admin
from django.conf import settings
# from django.conf.urls import include, url, path
from django.urls import re_path, include
from django.conf.urls.static import static
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

# User Imports
from users.views.views import (
    RegistrationView, LoginView, ForgetPassword,
    AgreementView, ResetPasswordView, ChangeUserPasswordView,
    UserCertificateView, CandidateActivationView, TestView, CalculateResult,
    TestInstructionView, CompanyAdvertisement)

from users.views.admin_view import AdminForgotPassword, AdminResetPasswordView, UserDetailView

from users.views.profile_view import (ProfileView,
                                      AddProfileImageView, UploadResumeView, ShowResumeView,
                                      EmploymentHistoryView, EducationalDetails,)

from users.views.training_view import (RecommendationCoursesView,
                                       SelectSkillsView, UserTrainingView, TrainingEpisodeView,)
# from users.views import CompanyAdvertisement

# Stats Imports
from stats.views import (CertificateView, CourseDetailView, CourseView, StatesView,
                         CitiesView, IndexView, AboutView, VisitorContactView,
                         IndustryView, SearchView, CompanyAddressView,)

# Company Imports
from company.views.views import (
    CompanyProfileView, CompanyDashboardView, SubscriptionView, AnnualSubscriptionView, UpdateCompanyImageView,
    MonthlySubscriptionView, SelectTechnologyStackView, TechnolgyStackView, RemoveTechnologyStack, SkillsListingView,
    CandidateResumeListingView, HireCandidateView, PreviousRequestView, HiredCandidateView,
    ReplacementRequestView, 
)
from company.views.auth import (
    CompanyRegistrationView, CompanyLoginView, CompanyForgotPasswordView, ChangePasswordView,
    LogoutView, CompanyResetPasswordView, CompanyUserActivationView, 
)
from company.views.payment import (
    payment_canceled, paypal_process_payment, payment_done,
)
from company.views import views
from company.views.views import RecommendationCandidateView
from django.contrib.auth import views as auth_views
from stats.views import *
urlpatterns = [

     # Admin  Urls
     path('admin/', admin.site.urls),
     path('password_reset/', AdminForgotPassword.as_view(), name='password_reset'),
     path('change/admin/password/', AdminResetPasswordView.as_view(), name='change_admin_password'), 
     
     # Stats related URLS
     path('', IndexView.as_view(), name="index"),
     path('city/', CitiesView.as_view(), name="city"),
     path('about/', AboutView.as_view(), name="about"),
     path("blog", BlogView.as_view(), name="blog"),
     path('state/', StatesView.as_view(), name="state"),
     path('course/', CourseView.as_view(), name="course"),
     path('search/', SearchView.as_view(), name="search"),
     path('industry/', IndustryView.as_view(), name='industry'),
     path('contact/', VisitorContactView.as_view(), name="contact"),
     path('register/', RegistrationView.as_view(), name="user_register"),
     path('certificate/', CertificateView.as_view(), name='certificate'),
     path('course-detail/<course_id>',
          CourseDetailView.as_view(), name="course_detail"),
     path('candidate/training-episode/',
          TrainingEpisodeView.as_view(), name='training_episode'),
     path('candidate/test/intructions/<course_id>',
          TestInstructionView.as_view(), name='test_instructions'),
     path('footer-address', CompanyAddressView.as_view(), name="company-address"),

     # Candidate related Urls
     path('profile/', ProfileView.as_view(), name="profile"),
     path('login/', LoginView.as_view(), name="user_sign_in"),
     path('candidate/test/', TestView.as_view(), name='candidate_test'),
     path('candidate/test/', TestView.as_view(), name='candidate_test_save'),
     path('select/skills/', SelectSkillsView.as_view(), name='select_skills'),
     path('profileimage/', AddProfileImageView.as_view(), name='profileimage'),
     path('forgot/password/', ForgetPassword.as_view(), name="forgot_password"),
     path('candidate/result', CalculateResult.as_view(), name='candidate_result'),
     path('candidate/activate/', CandidateActivationView.as_view(), name='activate'),
     path('candidate/agreement/', AgreementView.as_view(),
          name='candidate_agreement'),
     path('candidate/training/', UserTrainingView.as_view(),
          name='candidate_training'),
     path('candidate/reset/password/',
          ResetPasswordView.as_view(), name="reset_password"),
     path('candidate/show/resume', ShowResumeView.as_view(),
          name='candidate_display_resume'),
     path('candidate/training-episode/',
          TrainingEpisodeView.as_view(), name='training_episode'),
     path('candidate/certificate/', UserCertificateView.as_view(),
          name='candidate_certificate'),
     path('candidate/upload/resume/', UploadResumeView.as_view(),
          name='candidate_upload_resume'),
     path('candidate/change/password/',
          ChangeUserPasswordView.as_view(), name='user_change_password'),
     path('candidate/education/details', EducationalDetails.as_view(),
          name='candidate_education_details'),
     path('candidate/test/intructions/<course_id>',
          TestInstructionView.as_view(), name='test_instructions'),
     path('candidate/employment/history', EmploymentHistoryView.as_view(),
          name='candidate_employment_history'),

     path('candidate/recommendation_courses/',
          RecommendationCoursesView.as_view(), name='recommendation_courses'),
     path('candidate/advertisement/',CompanyAdvertisement.as_view(), name = 'candidate_advertisement'),

     # Company Related URlS
     path('logout/', LogoutView.as_view(), name="logout"),
     path("company/login/", CompanyLoginView.as_view(), name="company_login"),
     path("company/profile/", CompanyProfileView.as_view(), name="company_profile"),
     path("change/password/", ChangePasswordView.as_view(), name="change_password"),
     path("company/subscription/", SubscriptionView.as_view(), name="subscription"),
     path('company/reset/password', CompanyResetPasswordView.as_view(),
          name='company_reset_password'),
     path('company/user/activation/', CompanyUserActivationView.as_view(),
          name='company_user_activation'),
     path("company/forgot/password/", CompanyForgotPasswordView.as_view(),
          name="company_forgot_password"),
     path('company/dashboard/', CompanyDashboardView.as_view(),
          name="company_dashboard"),
     path("company/register/", CompanyRegistrationView.as_view(),
          name="company_register"),
     path("company/annual-subscription/",
          AnnualSubscriptionView.as_view(), name="annual-subscription"),
     path("company/monthly-subscription/",
          MonthlySubscriptionView.as_view(), name="monthly-subscription"),
     path("company/profile-pic/update", UpdateCompanyImageView.as_view(), 
          name="company-pic-update"),
     path("company/select-technolgy-stack", SelectTechnologyStackView.as_view(), 
          name='select-technolgy-stack'),
     path('company/view-monthlySubscription/', 
               TemplateView.as_view(template_name='company_user/hire_candidate/monthly_subscription.html'),
               name="monthly-subscription-view"),
     path('company/technolgy-stack/', TechnolgyStackView.as_view(), 
          name="technolgy-stack"),
     path('company/remove-technology-stack/', RemoveTechnologyStack.as_view(), 
          name="remove-technolgy-stack"),
     path('company/skills-listing-view/', SkillsListingView.as_view(), 
          name="skills-listing-view"),
     path('company/candidate-resume-listing/', CandidateResumeListingView.as_view(), 
          name="candidate-listing-view"),
     path('company/hiring-request-succeed/', 
               TemplateView.as_view(template_name='company_user/hire_candidate/hiring-request-succeed.html'),
               name="hiring-request-succeed/"),
     path('company/hire-candidate-request/', HireCandidateView.as_view(), name='hire-candidate-request'),
     path('company/previous-request/', 
               PreviousRequestView.as_view(),
               name="previous-request"),
     path(
          'company/hired-candidate/', 
          HiredCandidateView.as_view(),
          name='hired-candidate-list'
     ),
     path(
          'company/replacement-requests/',
          ReplacementRequestView.as_view(),
          name='replacement-request'
     ),
     path('company/advertisement/', views.AdvertisementView, name= 'advertisement_by_company'),
     path('company/send_request', views.Send_request, name= 'send_request'),
     # path('company/advertisement/', AdvertisementView.as_view(), name= 'advertisement_by_company '),
     path('company/recommendation_candidate/', RecommendationCandidateView.as_view(), name = 'recommendation_candidate_for_company'),
     path('company/hiring_candidate/', views.HiringCandidateView, name= 'hiring_candidate'),
     # Paypal Url Definitions
     path('paypal/', include("paypal.standard.ipn.urls")),
     path('payment/process/', paypal_process_payment, name='payment_process'),
     path('payment/done/', payment_done, name='payment_done'),
     path('payment/canceled/', payment_canceled, name='payment_canceled'),
]

urlpatterns = urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
