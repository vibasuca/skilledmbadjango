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

admin.site.site_header = "Skilled MBA Administration"
admin.site.site_title = "Skilled MBA Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", users_views.profile, name="account_profile"),
    path("login/", LoginView.as_view(), name="custom_login"),
    path("register/", SignupView.as_view(), name="custom_signup"),
    path("student-registration/", SignupView.as_view(), name="student_signup"),
    path(
        "",
        TemplateView.as_view(template_name="index.html"),
        name="index",
    ),
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
        "dashboard/my-courses/",
        TemplateView.as_view(template_name="dashboard/instructor/myCourses.html"),
        name="my_courses",
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
    path("media-library/", include("media_library.urls", namespace="media_library")),
    path("courses/", include("courses.urls", namespace="courses")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
