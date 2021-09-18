from race.models import Race
from django.urls import path
from .views import RaceDetailView, RaceIndexView

urlpatterns=[
    path('', RaceIndexView.as_view(), name="race_index"),
    path('<int:pk>/detail', RaceDetailView.as_view(), name="race_detail")
]