from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import CreateRaceForm
from .models import Category, RaceType
from place.models import Place
from account.models import Organizer

# Create your views here.
class CreateRaceView(TemplateView):
    def get(self, request):
        context = {
            "organizer" : Organizer.objects.get(pk=1),
            "places" : Place.objects.filter(is_active=True),
            "categories" : Category.objects.all(),
            "racetypes" : RaceType.objects.all(),
        }
        return render(request, "race/create.html", context=context)