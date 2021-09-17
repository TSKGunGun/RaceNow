from django.urls import path
from .views import CreatePlaceView, PlaceDetailView

urlpatterns = [
    path('create', CreatePlaceView.as_view(), name="place_create"),
    path('<int:pk>/detail', PlaceDetailView.as_view(), name="place_detail")
]