from django.views import generic
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView
from .models import Race, RaceType
from place.models import Place
from account.models import Organizer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CreateRaceForm
from django.urls import reverse

# Create your views here.
@method_decorator(login_required, name='dispatch')
class CreateRaceView(CreateView):
    template_name = "race/create.html"
    form_class = CreateRaceForm
    
    def get(self, request, *args, **kwargs):
        org = get_object_or_404(Organizer, pk=kwargs["org_id"])

        if not org.members.filter(id=request.user.id).exists() : 
            raise PermissionDenied
            
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object=None
        org = get_object_or_404(Organizer, pk=kwargs['org_id'])

        if not org.members.filter(id=request.user.id).exists() : 
            raise PermissionDenied

        form = self.get_form()
        if form.is_valid():
            race = Race(
                organizer = org,
                place = get_object_or_404(Place, pk=request.POST["place"]),
                name = request.POST["name"],
                url = request.POST["url"],
                racetype = get_object_or_404(RaceType, pk=request.POST["racetype"]),
            )   
            race.save()
            return redirect("race_detail", race.id)
        
        return self.form_invalid(form)

class RaceDetailView(DetailView):
    model = Race
    template_name = "race/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["IsMember"] =  self.object.organizer.members.filter(id=self.request.user.id).exists()

        return context

class RaceIndexView(ListView):
    model = Race
    template_name = "race/list.html"
