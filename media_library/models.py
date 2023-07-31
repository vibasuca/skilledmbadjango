import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def user_directory_path(instance, filename):
    # This function will store the file in the following format: media/user_<id>/<filename>_<short_uuid>.<ext>
    base_filename, ext = os.path.splitext(filename)
    short_uuid = uuid.uuid4().hex[:8]  # Use the first 8 characters of the UUID
    return f"media_library/user_{instance.user.id}/{base_filename}_{short_uuid}{ext}"


class Media(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s media: {self.file.name}"
