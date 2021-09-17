from race.models import Race
from django.urls import path
from .views import RaceDetailView

urlpatterns=[
    path('<int:pk>/detail', RaceDetailView.as_view(), name="race_detail")
]