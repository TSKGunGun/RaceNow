from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.fields.related import ForeignKey

User = get_user_model()

# Create your models here.
class Place(models.Model):
    owner = ForeignKey(User, verbose_name="owenr", null=False, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="name", null=False, max_length=100)
    address = models.CharField(verbose_name="address", null=False, max_length=200)
    url = models.URLField(verbose_name="homepage_url", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="active", null=False, default=True)
    image = models.ImageField(verbose_name="イメージ画像", upload_to='images/place/img', null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.id}:{self.name}"

    class Meta:
        db_table = "place"