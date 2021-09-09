from enum import unique
from re import T
from django.core.validators import ip_address_validator_map
from django.db import models
from django.contrib.auth.models import PermissionsMixin, UserManager, AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    username_validator = ASCIIUsernameValidator()
    username = models.CharField(_("username"), 
                    max_length=50, 
                    null=False, 
                    unique=True, 
                    validators=[username_validator],
                    help_text=_('Required. 50 characters or fewer. Letters, digits only.'),
                    error_messages={
                        'unique' : 'そのユーザー名は既に使われています。'
                    },
                )

    class Meta:
        db_table = 'users'
        swappable = 'AUTH_USER_MODEL'
