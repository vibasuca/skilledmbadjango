# Generated by Django 4.2.3 on 2023-08-10 05:49

import datetime
import django.core.validators
from django.db import migrations, models
import quizzes.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('summary', models.TextField(blank=True)),
                ('time_limit', models.DurationField(default=datetime.timedelta(0), help_text='Time limit for this quiz. 0 means no time limit.', validators=[quizzes.models.validate_max_duration, quizzes.models.validate_min_duration])),
                ('time_limit_unit', models.CharField(choices=[('W', 'Weeks'), ('D', 'Days'), ('H', 'Hours'), ('M', 'Minutes'), ('S', 'Seconds')], default='W', max_length=1)),
                ('hide_time_display', models.BooleanField(default=False)),
                ('feedback_mode', models.CharField(choices=[('D', 'Default'), ('R', 'Reveal Mode'), ('T', 'Retry Mode')], default='I', max_length=1)),
                ('max_attempts_allowed', models.PositiveIntegerField(default=10, help_text='Restriction on the number of attempts a student is allowed to take for this quiz. 0 for no limit')),
                ('passing_percentage', models.FloatField(default=80, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('max_questions', models.PositiveIntegerField(default=1, help_text='This amount of question will be available for students to answer, and question will comes randomly from all available questions belongs with a quiz, if this amount is greater than available question, then all questions will be available for a student to answer.', validators=[django.core.validators.MinValueValidator(1)])),
                ('auto_start', models.BooleanField(default=False, help_text='If you enable this option, the quiz will start automatically after the page is loaded.')),
                ('hide_question_no', models.BooleanField(default=False)),
                ('short_ans_char_limit', models.PositiveIntegerField(default=200, help_text='Student will place answer in short answer question type within this characters limit.')),
                ('long_ans_char_limit', models.PositiveIntegerField(default=500, help_text='Students will place the answer in the Open-Ended/Essay question type within this character limit.')),
            ],
        ),
        migrations.AddConstraint(
            model_name='quiz',
            constraint=models.CheckConstraint(check=models.Q(('passing_percentage__gte', 0.0), ('passing_percentage__lte', 100.0)), name='check_passing_percentage_range'),
        ),
        migrations.AddConstraint(
            model_name='quiz',
            constraint=models.CheckConstraint(check=models.Q(('max_questions__gte', 1)), name='check_max_questions_range'),
        ),
    ]
