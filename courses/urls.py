from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("create-course/", views.create_course, name="create_course"),
    path("update-course/<int:pk>/", views.update_course, name="update_course"),
]
