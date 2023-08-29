"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from allauth.account.views import LoginView, SignupView
from users import views as users_views
from courses import views as courses_views

admin.site.site_header = "Skilled MBA Administration"
admin.site.site_title = "Skilled MBA Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", users_views.profile, name="account_profile"),
    path("ajax-login/", users_views.AjaxLoginView.as_view(), name="ajax_login"),
    path("ajax-signup/", users_views.AjaxSignupView.as_view(), name="ajax_signup"),
    path(
        "",
        courses_views.index,
        name="index",
    ),
    path(
        "contact/",
        TemplateView.as_view(template_name="sitePages/contactUs.html"),
        name="contact_us",
    ),
    path("media-library/", include("media_library.urls", namespace="media_library")),
    path("courses/", include("courses.urls", namespace="courses")),
    path("", include("users.urls", namespace="users")),
    path("quizzes/", include("quizzes.urls", namespace="quizzes")),
]

# For checking static files in developement only
urlpatterns += [
    path(
        "dashboard/analytics/",
        TemplateView.as_view(template_name="dashboard/instructor/analytics.html"),
        name="analytics",
    ),
    path(
        "dashboard/announcements/",
        TemplateView.as_view(template_name="dashboard/instructor/announcements.html"),
        name="announcements",
    ),
    path(
        "dashboard/quiz-attempts/",
        TemplateView.as_view(template_name="dashboard/instructor/quizAttempts.html"),
        name="quiz_attempts",
    ),
    path(
        "dashboard/withdrawals/",
        TemplateView.as_view(template_name="dashboard/instructor/withdrawals.html"),
        name="withdrawals",
    ),
    path(
        "course-details/",
        TemplateView.as_view(template_name="sitePages/courseDetails.html"),
        name="course_details",
    ),
    path(
        "course-list/",
        TemplateView.as_view(template_name="sitePages/courseList.html"),
        name="course_list",
    ),
    path(
        "course-assignment/",
        TemplateView.as_view(template_name="courseContents/assignment.html"),
        name="course_assignment",
    ),
    path(
        "course-lesson/",
        TemplateView.as_view(template_name="courseContents/lesson.html"),
        name="course_lesson",
    ),
    path(
        "course-quiz/",
        TemplateView.as_view(template_name="courseContents/quiz.html"),
        name="course_quiz",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
