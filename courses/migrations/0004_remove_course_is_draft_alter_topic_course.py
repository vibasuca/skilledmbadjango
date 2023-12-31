# Generated by Django 4.2.3 on 2023-08-02 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_assignment_lesson_topic_alter_course_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='is_draft',
        ),
        migrations.AlterField(
            model_name='topic',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='courses.course'),
        ),
    ]
