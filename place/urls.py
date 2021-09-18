from django.urls import path
from .views import CreatePlaceView, PlaceDetailView, PlaceIndexView

urlpatterns = [
    path('', PlaceIndexView.as_view(), name="place_index"),
    path('create', CreatePlaceView.as_view(), name="place_create"),
    path('<int:pk>/detail', PlaceDetailView.as_view(), name="place_detail")
]