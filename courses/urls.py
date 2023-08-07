from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("create-course/", views.create_course, name="create_course"),
    path("update-course/<int:pk>/", views.update_course, name="update_course"),
    path("list-topics/<int:course_pk>/", views.list_topics, name="list_topics"),
    path("update-topic/<int:pk>/", views.update_topic, name="update_topic"),
    path("create-topic/<int:course_pk>/", views.create_topic, name="create_topic"),
    path("create-lesson/<int:topic_pk>/", views.create_lesson, name="create_lesson"),
    path(
        "create-assignment/<int:topic_pk>/",
        views.create_assignment,
        name="create_assignment",
    ),
    path("update-lesson/<int:pk>/", views.update_lesson, name="update_lesson"),
    path(
        "update-assignment/<int:pk>/", views.update_assignment, name="update_assignment"
    ),
    path(
        "list-topic-item/<int:topic_pk>/",
        views.list_topic_items,
        name="list_topic_items",
    ),
]
