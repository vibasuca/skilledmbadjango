from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path(
        "accounts/become-instructor/", views.become_instructor, name="become_instructor"
    ),
    path(
        "instructor-registration/",
        views.InstructorSignupView.as_view(),
        name="instructor_signup",
    ),
]
