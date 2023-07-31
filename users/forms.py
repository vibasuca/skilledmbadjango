from allauth.account.forms import SignupForm
from django import forms
from .models import User


class EmailAsTextInput(forms.EmailInput):
    input_type = "text"


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "First Name"}),
    )
    last_name = forms.CharField(
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Last Name"}),
    )
    email = forms.EmailField(widget=EmailAsTextInput(attrs={"placeholder": "E-Mail"}))

    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "profile_pic",
            "cover_pic",
            "display_name_format",
            "first_name",
            "last_name",
            "job_title",
            "phone",
            "bio",
        )