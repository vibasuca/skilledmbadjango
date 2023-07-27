# Generated by Django 4.2.3 on 2023-07-27 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cover_pic',
            field=models.ImageField(blank=True, upload_to='cover_pics'),
        ),
        migrations.AddField(
            model_name='user',
            name='display_name_format',
            field=models.CharField(choices=[('FL', 'First Last'), ('U', 'Username'), ('F', 'First'), ('L', 'Last'), ('LF', 'Last First')], default='FL', max_length=2),
        ),
    ]
