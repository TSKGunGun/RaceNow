# Generated by Django 3.2.6 on 2021-09-22 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('race', '0006_auto_20210922_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='race',
            name='is_regulationsetuped',
            field=models.BooleanField(default=False),
        ),
    ]
