
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
    class Meta:
        db_table = 'users'
        swappable = 'AUTH_USER_MODEL'
