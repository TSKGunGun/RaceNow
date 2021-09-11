
from asyncio.constants import DEBUG_STACK_DEPTH
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.utils import timezone

@deconstructible
class CustomUsernameValidator(validators.RegexValidator):
    regex = r'^[\w_]+\Z'
    message = 'ユーザ名は英数字,もしくはアンダーバー(_)のみが使用できます。'
    
    flags = 0

# Create your models here.
class User(AbstractUser):
    username_validator = CustomUsernameValidator()
    username = models.CharField("username", 
                    max_length=50, 
                    null=False, 
                    unique=True, 
                    validators=[username_validator],
                    help_text='ユーザ名は',
                    error_messages={
                        'unique' : 'そのユーザー名は既に使われています。'
                    },
                )
    email = models.EmailField('email_address', null=False)
    
    class Meta:
        db_table = 'users'
        swappable = 'AUTH_USER_MODEL'

#organizer
class Organizer(models.Model):
    owner = models.ForeignKey(User, verbose_name="owner",null=False, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="name", max_length=100, null=False)
    email_address = models.EmailField(verbose_name="email_address", null=False)
    is_active = models.BooleanField(verbose_name="is_active", default=True)
    url = models.URLField(verbose_name="homepage_url", null=False)

    class Meta:
        db_table = 'organizers'