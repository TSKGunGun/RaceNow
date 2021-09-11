from django.contrib import admin
from .models import Race, Category, RaceStatus, RaceType

# Register your models here.
admin.site.register(Race)
admin.site.register(Category)
admin.site.register(RaceStatus)
admin.site.register(RaceType)