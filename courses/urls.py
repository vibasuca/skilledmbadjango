from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("create-course/", views.create_course, name="create_course"),
    path("update-course/<int:pk>/", views.update_course, name="update_course"),
    path("list-topics/<int:course_pk>/", views.list_topics, name="list_topics"),
    path("update-topic/<int:pk>/", views.update_topic, name="update_topic"),
    path("create-topic/<int:course_pk>/", views.create_topic, name="create_topic"),
]
