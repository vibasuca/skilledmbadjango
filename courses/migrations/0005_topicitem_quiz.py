# Generated by Django 4.2.3 on 2023-08-10 06:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_alter_quiz_options_quiz_created_at_quiz_updated_at'),
        ('courses', '0004_remove_course_is_draft_alter_topic_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='topicitem',
            name='quiz',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='topic_item', to='quizzes.quiz'),
        ),
    ]
