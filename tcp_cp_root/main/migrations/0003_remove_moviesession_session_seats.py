# Generated by Django 4.0.1 on 2022-03-21 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_movie_movie_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='moviesession',
            name='session_seats',
        ),
    ]
