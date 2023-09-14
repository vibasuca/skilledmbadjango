from io import BytesIO
import os
import uuid
import cv2
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from moviepy.editor import VideoFileClip
from PIL import Image

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
    thumbnail = models.ImageField(
        upload_to="media-thumbnails/",
        default="media_library/default_thumbnail.png",
        blank=True,
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def get_size(self):
        value = self.file.size
        if value < 512000:
            value = value / 1024.0
            ext = "kb"
        elif value < 4194304000:
            value = value / 1048576.0
            ext = "mb"
        else:
            value = value / 1073741824.0
            ext = "gb"
        return "%s %s" % (str(round(value, 2)), ext)

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        super().save(*args, **kwargs)

        base_filename, ext = os.path.splitext(self.file.name)

        if is_new_instance:
            self.title = self.file.name.split("/")[-1]
            if ext in [".mp4", ".avi", ".mov", ".mkv", ".wmv"]:
                video_path = self.file.path
                thumbnail_bytes = self.generate_thumbnail(video_path)
                thumbnail_file = ContentFile(thumbnail_bytes, name="thumbnail.jpg")
                self.thumbnail.save("thumbnail.jpg", thumbnail_file, save=False)
            elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                thumbnail = self.file
                self.thumbnail.save("thumbnail.jpeg", thumbnail, save=False)
            super().save(*args, **kwargs)

    def generate_thumbnail(self, video_path):
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(0)  # Get the first frame as a thumbnail

        # Convert the frame to RGB color space
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Manually invert the colors
        inverted_frame_rgb = 255 - frame_rgb

        # Create the thumbnail from the inverted frame
        thumbnail = Image.fromarray(inverted_frame_rgb.astype("uint8"))
        thumbnail_io = BytesIO()
        thumbnail.save(thumbnail_io, format="JPEG")
        return thumbnail_io.getvalue()

    def __str__(self):
        return f"{self.user.username}'s media: {self.file.name}"
