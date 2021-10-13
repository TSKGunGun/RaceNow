from race.models import Race
from django.urls import path
from .views import EntrantIndexView, RaceDetailView, RaceIndexView, RegulationSetupView, \
                  AddEntrantView, deleteEntrant, deleteLap,startRace,inputResult,addLap, \
                  get_entrant_info, deleteLap, showResult, fixedRegulation, finishRace,setDNF, unsetDNF, \
                  EntrantIndexView, uploadEntrantCSVFile, EditEntrantView, deleteEntrant

urlpatterns=[
    #Details
    path('', RaceIndexView.as_view(), name="race_index"),
    path('<int:pk>/detail', RaceDetailView.as_view(), name="race_detail"),
    path('<int:pk>/setupregulations', RegulationSetupView.as_view(), name="regulations_setup"),

    #Change Status
    path('<int:pk>/fixedregulation', fixedRegulation, name="race_fixedregulation" ),
    path('<int:pk>/finishrace', finishRace, name="race_finishrace" ),
    path('<int:pk>/startrace', startRace, name="race_start" ),

    #Entrants
    path('<int:pk>/entrants/', EntrantIndexView.as_view(), name="entrant_index"),
    path('<int:pk>/entrants/add', AddEntrantView.as_view(), name="add_entrant" ),
    path('<int:pk>/entrants/<int:ent_pk>/edit', EditEntrantView.as_view(), name="edit_entrant" ),
    path('<int:pk>/entrants/<int:ent_pk>/delete', deleteEntrant, name="delete_entrant" ),
    path('<int:pk>/entrants/uploadEntrantCSVFile', uploadEntrantCSVFile, name="entrant_uploadCSV"),

    #InputResult
    path('<int:pk>/inputresult', inputResult, name="input_result" ),
    path('<int:pk>/inputresult/addlap', addLap, name="add_lap" ),
    path('<int:pk>/inputresult/deletelap', deleteLap, name="delete_lap" ),
    path('<int:pk>/inputresult/setDNF', setDNF, name="race_setdnf" ),
    path('<int:pk>/inputresult/unsetDNF', unsetDNF, name="race_unsetdnf" ),

    #ShowResult
    path('<int:pk>/showresult', showResult, name="show_result" ),
    
    #APIs
    path('entrants/<int:pk>/getinfo', get_entrant_info)
]
