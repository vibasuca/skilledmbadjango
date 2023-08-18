from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    path("mark-answer/<int:attempt_pk>/", views.mark_answer, name="mark_answer"),
    path("submit-answer/<int:attempt_pk>/", views.submit_answer, name="submit_answer"),
]
