from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CourseForm
from .models import *


@login_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect("courses:create_course")
    else:
        form = CourseForm()
    return render(request, "courses/create_course.html", {"form": form})


@login_required
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("courses:update_course", pk=course.pk)
    else:
        form = CourseForm(instance=course)

    return render(request, "courses/create_course.html", {"form": form})
