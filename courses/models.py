from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from media_library.models import Media

User = get_user_model()

DIFFICULTY_LEVEL_CHOICES = (
    ("A", "All Levels"),
    ("B", "Beginner"),
    ("I", "Intermediate"),
    ("E", "Expert"),
)

LANGUAGE_CHOICES = (
    ("E", "English"),
    ("F", "French"),
    ("G", "German"),
    ("I", "Italian"),
    ("J", "Japanese"),
    ("K", "Korean"),
    ("R", "Russian"),
    ("S", "Spanish"),
)


def validate_max_duration(value):
    if value > timedelta(hours=1000):
        raise ValidationError("Maximum duration is 1000 hours.")


def validate_min_duration(value):
    if value < timedelta(seconds=0):
        raise ValidationError("Minimum duration is 0 second.")


class CourseTag(models.Model):
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


class CourseCategory(models.Model):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="subcategories",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("title",)
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    max_students = models.PositiveIntegerField(
        default=0,
        help_text="Number of students that can enrol in this course. Set 0 for no limits.",
    )
    difficulty_level = models.CharField(
        max_length=1, choices=DIFFICULTY_LEVEL_CHOICES, default="A"
    )
    is_public = models.BooleanField(
        default=False, help_text="Make This Course Public. No enrollment required."
    )
    enable_qa = models.BooleanField(
        default=False, help_text="Enable Q&A section for your course"
    )
    language = models.CharField(max_length=1, choices=LANGUAGE_CHOICES, default="E")
    category = models.ForeignKey(
        CourseCategory, on_delete=models.CASCADE, related_name="courses"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    thumbnail = models.ForeignKey(
        Media, on_delete=models.CASCADE, related_name="thumbnail_for_courses"
    )
    instructors = models.ManyToManyField(User, related_name="courses_as_instructor")
    attachments = models.ManyToManyField(Media, related_name="attachments_for_courses")
    what_will_i_learn = models.TextField(
        blank=True, help_text="Write here the course benefits (One per line)"
    )
    target_audience = models.TextField(
        blank=True,
        help_text="Specify the target audience that will benefit the most from the course. (One line per target audience.)",
    )
    duration = models.DurationField(
        default=timedelta(hours=1),
        validators=[validate_max_duration, validate_min_duration],
    )
    materials_included = models.TextField(
        blank=True,
        help_text="A list of assets you will be providing for the students in this course (One per line)",
    )
    requirements = models.TextField(
        blank=True,
        help_text="Additional requirements or special instructions for the students (One per line)",
    )
    tags = models.ManyToManyField(CourseTag, related_name="courses")
    prerequisite_courses = models.ManyToManyField(
        "self", symmetrical=False, related_name="prerequisite_for_courses"
    )
    is_draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-updated_at",)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s course: {self.title}"
