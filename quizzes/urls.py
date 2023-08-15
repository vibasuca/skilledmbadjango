from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    path("mark-answer/<int:pk>/", views.mark_answer, name="mark_answer"),
]
