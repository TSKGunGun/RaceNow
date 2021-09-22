from django.contrib import admin
from .models import Race, Category, RaceStatus, RaceType, Entrant, Entrant_Member, Lap

# Register your models here.
admin.site.register(Race)
admin.site.register(Category)
admin.site.register(RaceStatus)
admin.site.register(RaceType)
admin.site.register(Entrant)
admin.site.register(Entrant_Member)
admin.site.register(Lap)