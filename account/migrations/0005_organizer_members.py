# Generated by Django 3.2.6 on 2021-09-14 05:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizer',
            name='members',
            field=models.ManyToManyField(related_name='organizers', related_query_name='organizer', to=settings.AUTH_USER_MODEL),
        ),
    ]
