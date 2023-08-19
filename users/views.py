from allauth.account.views import SignupView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from courses.models import Course
from .forms import CustomSignupForm, UserUpdateForm
from .models import User


@login_required
def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")

            return redirect("account_profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "account/profile.html", {"form": form})


class InstructorSignupView(SignupView):
    form_class = CustomSignupForm
    template_name = "account/instructor_signup.html"


@require_POST
@login_required
def become_instructor(request):
    request.user.is_instructor = True
    request.user.save()
    messages.success(request, "You are now an instructor.")
    redirect_url = reverse("account_profile")
    return JsonResponse({"success": True, "redirect_url": redirect_url})


@login_required
def search_instructors(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, user=request.user)
    instructor_ids = course.instructors.values_list("id", flat=True)
    users = (
        User.objects.exclude(id=request.user.id)
        .exclude(id__in=instructor_ids)
        .filter(is_instructor=True)
        .annotate(
            full_name=Concat(
                F("first_name"),
                Value(" "),
                F("last_name"),
                output_field=CharField(),
            )
        )
    )
    search_query = request.GET.get("q", "")
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | Q(full_name__icontains=search_query)
        )
    users = users.values("id", "first_name", "last_name", "email")
    return JsonResponse({"data": list(users)})
