import os
import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

User = get_user_model()


def validate_file_extension(value):
    valid_extensions = [
        # Images
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        # Videos
        "mp4",
        "avi",
        "mov",
        "mkv",
        "wmv",
        # Audio
        "mp3",
        "wav",
        "ogg",
        "flac",
        "aac",
        # Zip archives
        "zip",
        "rar",
        # Text files
        "txt",
        "csv",
        "log",
        "md",
        # PDF files
        "pdf",
    ]

    validator = FileExtensionValidator(allowed_extensions=valid_extensions)

    try:
        validator(value)
    except ValidationError as e:
        print(e)
        raise ValidationError(
            "File type not supported. Allowed file types: "
            + ", ".join(valid_extensions)
        )


def user_directory_path(instance, filename):
    # This function will store the file in the following format: media/user_<id>/<filename>_<short_uuid>.<ext>
    base_filename, ext = os.path.splitext(filename)
    short_uuid = uuid.uuid4().hex[:8]  # Use the first 8 characters of the UUID
    return f"media_library/user_{instance.user.id}/{base_filename}_{short_uuid}{ext}"


class Media(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(
        upload_to=user_directory_path, validators=[validate_file_extension]
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.username}'s media: {self.file.name}"
