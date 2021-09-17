from django.urls import path
from .views import CreateRaceView

urlpatterns=[
    path('create', CreateRaceView.as_view(), name="race_create")
]