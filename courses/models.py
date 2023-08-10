from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from media_library.models import Media
from quizzes.models import Quiz

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

TIME_LIMIT_UNIT_CHOICES = (
    ("W", "Weeks"),
    ("D", "Days"),
    ("H", "Hours"),
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
        CourseCategory,
        on_delete=models.CASCADE,
        related_name="courses",
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    thumbnail = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name="thumbnail_for_courses",
        null=True,
        blank=True,
    )
    instructors = models.ManyToManyField(
        User, related_name="courses_as_instructor", blank=True
    )
    attachments = models.ManyToManyField(
        Media, related_name="attachments_for_courses", blank=True
    )
    what_will_i_learn = models.TextField(
        blank=True, help_text="Write here the course benefits (One per line)"
    )
    target_audience = models.TextField(
        blank=True,
        help_text="Specify the target audience that will benefit the most from the course. (One line per target audience.)",
    )
    duration = models.DurationField(
        default=timedelta(),
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
    tags = models.ManyToManyField(CourseTag, related_name="courses", blank=True)
    prerequisite_courses = models.ManyToManyField(
        "self", symmetrical=False, related_name="prerequisite_for_courses", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-updated_at",)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s course: {self.title}"


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order",)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    feature_image = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name="feature_image_for_topics",
        null=True,
        blank=True,
    )
    attachments = models.ManyToManyField(
        Media, related_name="attachments_for_lessons", blank=True
    )
    enable_preview = models.BooleanField(
        default=False,
        help_text="If checked, any users/guest can view this lesson without enroll course",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    attachments = models.ManyToManyField(
        Media, related_name="attachments_for_assignments", blank=True
    )
    time_limit = models.DurationField(
        default=timedelta(),
        validators=[validate_max_duration, validate_min_duration],
    )
    time_limit_unit = models.CharField(
        max_length=1, choices=TIME_LIMIT_UNIT_CHOICES, default="W"
    )
    total_points = models.PositiveIntegerField(default=10)
    min_pass_points = models.PositiveIntegerField(default=5)
    max_file_uploads = models.PositiveIntegerField(
        default=1,
        help_text="Define the number of files that a student can upload in this assignment. Input 0 to disable the option to upload.",
    )
    file_size_limit = models.PositiveIntegerField(
        default=2, help_text="Define maximum file size attachment in MB"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return self.title


class TopicItem(models.Model):
    """
    This model is used to store the lesson, assignment, quiz for a topic and acts as a manager.
    """

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="items")
    sort_order = models.PositiveIntegerField(default=0)
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name="topic_item",
        null=True,
        blank=True,
    )
    assignment = models.OneToOneField(
        Assignment,
        on_delete=models.CASCADE,
        related_name="topic_item",
        null=True,
        blank=True,
    )
    quiz = models.OneToOneField(
        Quiz,
        on_delete=models.CASCADE,
        related_name="topic_item",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("sort_order",)

    def __str__(self):
        if self.lesson:
            return f"Lesson: {self.lesson.title}"
        elif self.assignment:
            return f"Assignment: {self.assignment.title}"
        elif self.quiz:
            return f"Quiz: {self.quiz.title}"
        return "Unknown Topic Item"
