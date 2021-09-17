from django.urls import path
from .views import CreateRaceView

urlpatterns=[
    path('<int:org_id>/detail', CreateRaceView.as_view(), name="race_detail")
]