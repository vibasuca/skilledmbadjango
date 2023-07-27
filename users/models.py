from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

NAME_FORMAT_CHOICES = (
    ("FL", "First Last"),
    ("U", "Username"),
    ("F", "First"),
    ("L", "Last"),
    ("LF", "Last First"),
)


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    job_title = models.CharField(max_length=150, blank=True)
    phone = models.CharField(
        max_length=15,
        validators=[
            MinLengthValidator(4),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
        ],
        blank=True,
    )
    profile_pic = models.ImageField(upload_to="profile_pics", blank=True)
    cover_pic = models.ImageField(upload_to="cover_pics", blank=True)
    bio = models.TextField(max_length=10000, blank=True)
    display_name_format = models.CharField(
        max_length=2, choices=NAME_FORMAT_CHOICES, default="FL"
    )
    is_student = models.BooleanField(default=True)
    is_instructor = models.BooleanField(default=False)
