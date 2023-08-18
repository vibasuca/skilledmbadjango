from allauth.account.forms import SignupForm, LoginForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
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
    account_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    email = forms.EmailField(widget=EmailAsTextInput(attrs={"placeholder": "E-Mail"}))
    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def save(self, request):
        user = super().save(request)
        if self.cleaned_data["account_type"] == "instructor":
            user.is_instructor = True
            user.save()
        return user


class CustomLoginForm(LoginForm):
    pass
    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)


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
