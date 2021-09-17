from django.core.exceptions import PermissionDenied
from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from .models import Category, Race, RaceStatus, RaceType
from place.models import Place
from account.models import Organizer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
def race_validation(race):
        return True

@method_decorator(login_required, name='dispatch')
class CreateRaceView(TemplateView):
    def get(self, request, org_id):
        org = get_object_or_404(Organizer, pk=org_id)

        if not org.members.filter(id=request.user.id).exists() : 
            raise PermissionDenied
            
        context = {
            "organizer" : org,
            "places" : Place.objects.filter(is_active=True),
            "categories" : Category.objects.all(),
            "racetypes" : RaceType.objects.all(),
        }
        return render(request, "race/create.html", context=context)
    
    def post(self, request, org_id):
        org = get_object_or_404(Organizer, pk=request.POST['organizer'])

        if not org.members.filter(id=request.user.id).exists() : 
            raise PermissionDenied

        race = Race(
            organizer = org,
            place = get_object_or_404(Place, pk=request.POST["place"]),
            name = request.POST["name"],
            racetype = get_object_or_404(RaceType, pk=request.POST["racetype"]),
            url = request.POST["url"],
        )

        if not race_validation(race) :
            pass

        race.save()
        return redirect("race_detail", pk=race.id)

class RaceDetailView(DetailView):
    model = Race
    template_name = "race/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["IsMember"] =  self.object.organizer.members.filter(id=self.request.user.id).exists()

        return context