from datetime import timedelta
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

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
        max_length=1, choices=FEEDBACK_MODE_CHOICES, default="I"
    )
    max_attempts_allowed = models.PositiveIntegerField(
        default=10,
        help_text="Restriction on the number of attempts a student is allowed to take for this quiz. 0 for no limit",
    )
    passing_percentage = models.FloatField(default=80)
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
