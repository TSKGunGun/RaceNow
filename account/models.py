
import re
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

@deconstructible
class CustomUsernameValidator(validators.RegexValidator):
    regex = r'^[\w_]+\Z'
    message = 'ユーザ名は英数字,もしくはアンダーバー(_)のみが使用できます。'
    
    flags = re.ASCII

# Create your models here.
class User(AbstractUser):
    username_validator = CustomUsernameValidator()
    username = models.CharField("ユーザー名", 
                    max_length=50, 
                    null=False, 
                    unique=True, 
                    validators=[username_validator],
                    help_text='ユーザ名は50文字以下で、英数字,もしくはアンダーバー(_)のみが使用できます。',
                    error_messages={
                        'unique' : 'そのユーザー名は既に使われています。'
                    },
                )
    email = models.EmailField('メールアドレス', null=False)
    
    class Meta:
        db_table = 'users'
        swappable = 'AUTH_USER_MODEL'

#organizer
class Organizer(models.Model):
    owner = models.ForeignKey(User, verbose_name="オーナー", related_name="owner", null=False, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="主催団体名", max_length=100, null=False)
    email_address = models.EmailField(verbose_name="メールアドレス", null=False)
    is_active = models.BooleanField(verbose_name="有効フラグ", default=True)
    url = models.URLField(verbose_name="ホームページURL", null=False)
    members = models.ManyToManyField(User, related_name="organizers", related_query_name="organizer")

    def is_member(self, user):
        return self.members.filter(pk=user.id).exists()

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'organizers'

