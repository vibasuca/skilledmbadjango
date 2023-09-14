from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # Main site
    path("<int:pk>/<str:slug>/", views.course_details, name="course_details"),
    path("enroll-course/<int:course_pk>/", views.enroll_course, name="enroll_course"),
    path("lessons/<int:pk>/", views.lesson_details, name="lesson_details"),
    path(
        "lessons/<int:pk>/mark-complete/",
        views.mark_lesson_complete,
        name="mark_lesson_complete",
    ),
    path("assignments/<int:pk>/", views.assignment_details, name="assignment_details"),
    path("quizzes/<int:pk>/", views.quiz_details, name="quiz_details"),
    # Dashboard
    path("my-courses/", views.list_courses_published, name="list_courses_published"),
    path(
        "my-courses/pending-courses/",
        views.list_courses_pending,
        name="list_courses_pending",
    ),
    path(
        "my-courses/draft-courses/", views.list_courses_draft, name="list_courses_draft"
    ),
    path("create-course/", views.create_course, name="create_course"),
    path("update-course/<int:pk>/", views.update_course, name="update_course"),
    path("list-topics/<int:course_pk>/", views.list_topics, name="list_topics"),
    path("update-topic/<int:pk>/", views.update_topic, name="update_topic"),
    path("create-topic/<int:course_pk>/", views.create_topic, name="create_topic"),
    path("create-lesson/<int:topic_pk>/", views.create_lesson, name="create_lesson"),
    path("create-quiz/<int:topic_pk>/", views.create_quiz, name="create_quiz"),
    path(
        "create-question/<int:quiz_pk>/", views.create_question, name="create_question"
    ),
    path("create-option/<int:question_pk>/", views.create_option, name="create_option"),
    path(
        "create-assignment/<int:topic_pk>/",
        views.create_assignment,
        name="create_assignment",
    ),
    path("update-lesson/<int:pk>/", views.update_lesson, name="update_lesson"),
    path(
        "update-assignment/<int:pk>/", views.update_assignment, name="update_assignment"
    ),
    path("update-quiz/<int:pk>/", views.update_quiz, name="update_quiz"),
    path("update-question/<int:pk>/", views.update_question, name="update_question"),
    path("update-option/<int:pk>/", views.update_option, name="update_option"),
    path(
        "list-topic-item/<int:topic_pk>/",
        views.list_topic_items,
        name="list_topic_items",
    ),
    path(
        "list-questions/<int:quiz_pk>/",
        views.list_questions,
        name="list_questions",
    ),
    path(
        "list-options/<int:question_pk>/",
        views.list_options,
        name="list_options",
    ),
]
