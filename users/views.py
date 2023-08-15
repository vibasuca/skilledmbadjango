from allauth.account.views import SignupView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import CustomSignupForm, UserUpdateForm


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
