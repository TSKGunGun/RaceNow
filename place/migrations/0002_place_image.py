# Generated by Django 3.2.6 on 2021-10-05 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/place/img', verbose_name='イメージ画像'),
        ),
    ]
