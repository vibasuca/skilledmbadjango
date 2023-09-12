from datetime import timedelta
import random
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from media_library.models import Media

User = get_user_model()

TIME_LIMIT_UNIT_CHOICES = (
    ("W", "Weeks"),
    ("D", "Days"),
    ("H", "Hours"),
    ("M", "Minutes"),
    ("S", "Seconds"),
)

FEEDBACK_MODE_CHOICES = (
    ("D", "Default"),  # Answers shown after quiz is finished
    ("R", "Reveal Mode"),  # Show result after the attempt.
    (
        "T",
        "Retry Mode",
    ),  # Reattempt quiz any number of times. Define Attempts Allowed below.
)

ANSWER_STATUS_CHOICES = (
    ("C", "Correct"),
    ("I", "Incorrect"),
    ("P", "Pending"),
)

QUESTION_TYPE_CHOICES = (
    ("TF", "True/False"),
    ("SC", "Single Choice"),
    ("MC", "Multiple Choice"),
    ("OE", "Open Ended"),
    ("FB", "Fill in the Blanks"),
    ("SA", "Short Answer"),
    ("M", "Matching"),
    ("IM", "Image Matching"),
    ("IA", "Image Answering"),
    ("O", "Ordering"),
)

DISPLAY_FORMAT_CHOICES = (
    ("T", "Only Text"),
    ("I", "Only Image"),
    ("B", "Text & Image both"),
)


def validate_max_duration(value):
    if value > timedelta(hours=1000):
        raise ValidationError("Maximum duration is 1000 hours.")


def validate_min_duration(value):
    if value < timedelta(seconds=0):
        raise ValidationError("Minimum duration is 0 second.")


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    time_limit = models.DurationField(
        default=timedelta(),
        validators=[validate_max_duration, validate_min_duration],
        help_text="Time limit for this quiz. 0 means no time limit.",
    )
    time_limit_unit = models.CharField(
        max_length=1, choices=TIME_LIMIT_UNIT_CHOICES, default="W"
    )
    hide_time_display = models.BooleanField(default=False)
    feedback_mode = models.CharField(
        max_length=1, choices=FEEDBACK_MODE_CHOICES, default="D"
    )
    max_attempts_allowed = models.PositiveIntegerField(
        default=10,
        help_text="Restriction on the number of attempts a student is allowed to take for this quiz. 0 for no limit",
    )
    passing_percentage = models.FloatField(
        default=80, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_questions = models.PositiveIntegerField(
        default=1,
        help_text="This amount of question will be available for students to answer, and question will comes randomly from all available questions belongs with a quiz, if this amount is greater than available question, then all questions will be available for a student to answer.",
        validators=[MinValueValidator(1)],
    )
    # Advance Settings
    auto_start = models.BooleanField(
        default=False,
        help_text="If you enable this option, the quiz will start automatically after the page is loaded.",
    )
    hide_question_no = models.BooleanField(default=False)
    short_ans_char_limit = models.PositiveIntegerField(
        default=200,
        help_text="Student will place answer in short answer question type within this characters limit.",
    )
    long_ans_char_limit = models.PositiveIntegerField(
        default=500,
        help_text="Students will place the answer in the Open-Ended/Essay question type within this character limit.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(passing_percentage__gte=0.0)
                & models.Q(passing_percentage__lte=100.0),
                name="check_passing_percentage_range",
            ),
            models.CheckConstraint(
                check=models.Q(max_questions__gte=1), name="check_max_questions_range"
            ),
        ]
        ordering = ("-created_at",)
        verbose_name = "quiz"
        verbose_name_plural = "quizzes"

    def get_questions_count(self):
        return min(self.questions.count(), self.max_questions)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(
        max_length=2,
        choices=QUESTION_TYPE_CHOICES,
        default="TF",
    )
    answer_required = models.BooleanField(default=False)
    randomize_options = models.BooleanField(default=False)
    points = models.FloatField(default=1)
    display_points = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # For True/False Question Type
    tf_correct_answer = models.BooleanField(default=True)
    tf_true_first = models.BooleanField(default=True)  # Show True first or False first
    # For Fill in the Blanks Question Type
    fb_question_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Please make sure to use the {dash} variable in your question title to show the blanks in your question. You can use multiple {dash} variables in one question.",
    )
    fb_correct_answer = models.CharField(
        max_length=255,
        blank=True,
        help_text="Separate multiple answers by a vertical bar |. 1 answer per {dash} variable is defined in the question. Example: Apple | Banana | Orange",
    )

    class Meta:
        ordering = ("quiz", "sort_order")

    def __str__(self):
        return self.title


class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    type = models.CharField(
        max_length=2,
        choices=QUESTION_TYPE_CHOICES,
        default="TF",
    )
    title = models.CharField(max_length=255)  # Used by SC, MC, IM, IA Question Types
    image = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name="image_for_options",
        null=True,
        blank=True,
    )
    display_format = models.CharField(
        max_length=1,
        choices=DISPLAY_FORMAT_CHOICES,
        default="T",
    )
    is_correct = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)  # Also used by O Question Type
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # For Matching Question Type
    m_matched_ans_title = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("question", "sort_order")

    def __str__(self):
        return self.title


class Attempt(models.Model):
    enrollment = models.ForeignKey(
        "courses.Enrollment", on_delete=models.CASCADE, related_name="quiz_attempts"
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quiz_attempts"
    )
    seed = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    instructor_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-submitted_at", "-created_at")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.seed = random.randrange(10000)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quiz.title} - {self.user.username}"


class Answer(models.Model):
    attempt = models.ForeignKey(
        Attempt, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name="answers",
        null=True,
        blank=True,
    )
    # For True/False Question Type
    tf_answer = models.BooleanField(default=True)
    # For FB, SA, OE, M, IM Question Type
    answer_text = models.TextField(blank=True)
    # For Ordering Question Type
    o_answer_order = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=1,
        choices=ANSWER_STATUS_CHOICES,
        default="P",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("attempt", "o_answer_order")

    def __str__(self):
        return f"{self.question.title} - {self.attempt.user.username}"
