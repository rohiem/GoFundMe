# Generated by Django 3.1.5 on 2021-01-12 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_petition_likes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='petition',
            old_name='likes',
            new_name='follows',
        ),
    ]
