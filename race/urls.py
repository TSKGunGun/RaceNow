from race.models import Race
from django.urls import path
from .views import RaceDetailView, RaceIndexView, RegulationSetupView, AddEntrantView,startRace,inputResult

urlpatterns=[
    path('', RaceIndexView.as_view(), name="race_index"),
    path('<int:pk>/setupregulations', RegulationSetupView.as_view(), name="regulations_setup"),
    path('<int:pk>/detail', RaceDetailView.as_view(), name="race_detail"),
    path('<int:pk>/entrants/add', AddEntrantView.as_view(), name="add_entrant" ),
    path('<int:pk>/startrace', startRace, name="race_start" ),
    path('<int:pk>/inputresult', inputResult, name="input_result" )
]