# Generated by Django 3.2.6 on 2021-09-21 03:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20210921_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizer',
            name='email_address',
            field=models.EmailField(max_length=254, verbose_name='メールアドレス'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='有効フラグ'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='name',
            field=models.CharField(max_length=100, verbose_name='主催団体名'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL, verbose_name='オーナー'),
        ),
        migrations.AlterField(
            model_name='organizer',
            name='url',
            field=models.URLField(verbose_name='ホームページURL'),
        ),
    ]
