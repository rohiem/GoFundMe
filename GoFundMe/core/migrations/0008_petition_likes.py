# Generated by Django 3.1.5 on 2021-01-12 15:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0007_auto_20210112_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='petition',
            name='likes',
            field=models.ManyToManyField(related_name='petitions', to=settings.AUTH_USER_MODEL),
        ),
    ]