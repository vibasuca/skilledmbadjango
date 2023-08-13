# Generated by Django 4.2.3 on 2023-08-13 05:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_topicitem_quiz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignment',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ('course', 'sort_order')},
        ),
        migrations.AlterModelOptions(
            name='topicitem',
            options={'ordering': ('topic', 'sort_order')},
        ),
    ]
