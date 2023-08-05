from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets
    fieldsets[0][1]["fields"] += ("is_student", "is_instructor")
    fieldsets[1][1]["fields"] += ("profile_pic", "cover_pic", "job_title", "bio", "phone")


admin.site.register(User, CustomUserAdmin)
