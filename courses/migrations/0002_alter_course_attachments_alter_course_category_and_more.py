# Generated by Django 4.2.3 on 2023-07-31 14:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media_library', '0003_alter_media_options_alter_media_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='attachments',
            field=models.ManyToManyField(blank=True, related_name='attachments_for_courses', to='media_library.media'),
        ),
        migrations.AlterField(
            model_name='course',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='courses.coursecategory'),
        ),
        migrations.AlterField(
            model_name='course',
            name='instructors',
            field=models.ManyToManyField(blank=True, related_name='courses_as_instructor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='course',
            name='prerequisite_courses',
            field=models.ManyToManyField(blank=True, related_name='prerequisite_for_courses', to='courses.course'),
        ),
        migrations.AlterField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='courses', to='courses.coursetag'),
        ),
        migrations.AlterField(
            model_name='course',
            name='thumbnail',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='thumbnail_for_courses', to='media_library.media'),
        ),
    ]