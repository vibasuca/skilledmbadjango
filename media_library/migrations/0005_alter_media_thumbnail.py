# Generated by Django 4.2.3 on 2023-09-14 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_library', '0004_media_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='thumbnail',
            field=models.ImageField(blank=True, default='media_library/default_thumbnail.png', upload_to='media-thumbnails/'),
        ),
    ]
