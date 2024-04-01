import cloudinary
import datetime
import cloudinary.uploader

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from stats.models import (About, CompanyAddress, Course, CourseVideos,
                          HomeVideos, VistorContact, Home, Welcome, Test, Questions, AnswerChoices, Blog)


# Register your models here.
admin.site.register(About)
admin.site.register(Blog)


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    search_fields = ("titles", )


@admin.register(HomeVideos)
class HomeVideoAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if change and (obj.video_url is not None):
            # Get Public Id from url
            public_id = obj.video_url.rsplit('/')[-1].split('.')[0]
            # Delete Existing video from Cloudinary
            res_des = cloudinary.uploader.destroy(
                public_id='home_video/' + public_id,
                resource_type='video',
            )
        # Upload Video in cloudinary
        res = cloudinary.uploader.upload_large(
            request.FILES.get('video'),
            resource_type="video",
            chunk_size=6000000,
            folder='home_video/'
        )
        obj.video_url = res.get('secure_url')
        obj.duration = datetime.timedelta(seconds=int(res.get('duration')))
        obj.video = None
        super(HomeVideoAdmin, self).save_model(request, obj, form, change)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_title',
                 'chapters_count', 'video', 'view_test', 'course_chapter' )
    list_per_page = 10

    @admin.display(ordering='course_title', description='No of chapters')
    def chapters_count(self, obj):
        return obj.chapters_count()

    @admin.display(ordering='course_title', description='Video')
    def video(self, obj):
        return format_html(
            '<a href="{}" title="Address list" alt="Address List">{}</a>'.format(
                str(obj.video_url),
				'<i class="fa fa-video-camera"></i>'
            )
        )

    @admin.display(ordering='course_title', description='View Test')
    def view_test(self, obj):
        return format_html(
            '<a href="{}" title="Candidate Detail" alt="Candidate Detail">{}</a> '.format(
                reverse('admin:stats_test_changelist') +
                '?course_id=' + str(obj.id),
                '<i class="fa fa-info-circle" style="color:black"></i>'
            )
        )
    
    @admin.display(ordering='id', description='Chapters')
    def course_chapter(self, obj):
        return format_html(
            '<a href="{}" title="Address list" alt="Address List">{}</a>'.format(
                reverse(
                    "admin:stats_coursevideos_changelist",
                ) + 
                '?courses_id=' + str(obj.id),
                '<i class="fa fa-external-link"></i>'
            )
        )

    def save_model(self, request, obj, form, change):
        if change and (obj.video_url is not None):
            # Get Public Id from url
            public_id = obj.video_url.rsplit('/')[-1].split('.')[0]
            # Delete Existing video from Cloudinary
            res_des = cloudinary.uploader.destroy(
                public_id='courses/' + public_id,
                resource_type='video',
            )
        # Upload Video in cloudinary
        res = cloudinary.uploader.upload_large(
            request.FILES.get('course_vid'),
            resource_type="video",
            chunk_size=6000000,
            folder='course/'
        )
        obj.video_url = res.get('secure_url')
        obj.duration = datetime.timedelta(seconds=int(res.get('duration')))
        obj.course_vid = None
        super(CourseAdmin, self).save_model(request, obj, form, change)


@admin.register(CourseVideos)
class CourseVideosAdmin(admin.ModelAdmin):
    list_display = ('title','duration', 'video')
    list_per_page = 10


    @admin.display(ordering='title', description='Video')
    def video(self, obj):
        return format_html(
            '<a href="{}" title="Chapter video" alt="Chapter video">{}</a>'.format(
                str(obj.video_url),
				'<i class="fa fa-video-camera"></i>'
            )
        )

    def save_model(self, request, obj, form, change):
        if change and (obj.video_url is not None):
            # Get Public Id from url
            public_id = obj.video_url.rsplit('/')[-1].split('.')[0]
            # Delete Existing video from Cloudinary
            res_des = cloudinary.uploader.destroy(
                public_id='course/' + obj.courses.course_title + '/' + public_id,
                resource_type='video',
            )
        # Upload Video in cloudinary
        res = cloudinary.uploader.upload_large(
            request.FILES.get('video'),
            resource_type="video",
            chunk_size=6000000,
            folder='course/' + obj.courses.course_title + '/'
        )
        obj.video_url = res.get('secure_url')
        obj.duration = datetime.timedelta(seconds=int(res.get('duration')))
        obj.video = None
        super(CourseVideosAdmin, self).save_model(request, obj, form, change)


admin.site.register(CompanyAddress)
admin.site.register(VistorContact)
admin.site.register(Welcome)
admin.site.register(Test)
admin.site.register(Questions)
admin.site.register(AnswerChoices)
