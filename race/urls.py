from race.models import Race
from django.urls import path
from .views import RaceDetailView, RaceIndexView, RegulationSetupView, \
                  AddEntrantView, deleteLap,startRace,inputResult,addLap, get_entrant_info, deleteLap, showResult, fixedRegulation, finishRace

urlpatterns=[
    path('', RaceIndexView.as_view(), name="race_index"),
    path('<int:pk>/setupregulations', RegulationSetupView.as_view(), name="regulations_setup"),
    path('<int:pk>/detail', RaceDetailView.as_view(), name="race_detail"),
    path('<int:pk>/entrants/add', AddEntrantView.as_view(), name="add_entrant" ),
    path('<int:pk>/fixedregulation', fixedRegulation, name="race_fixedregulation" ),
    path('<int:pk>/finishrace', finishRace, name="race_finishrace" ),
    path('<int:pk>/startrace', startRace, name="race_start" ),
    path('<int:pk>/inputresult', inputResult, name="input_result" ),
    path('<int:pk>/showresult', showResult, name="show_result" ),
    path('<int:pk>/inputresult/addlap', addLap, name="add_lap" ),
    path('<int:pk>/inputresult/deletelap', deleteLap, name="delete_lap" ),
    
    #APIs
    path('entrants/<int:pk>/getinfo', get_entrant_info)
]
