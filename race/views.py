from django.core.checks import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.base import TemplateView
from .models import Race, RaceType
from place.models import Place
from account.models import Organizer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import CreateRaceForm, Regulation_XC_Form, AddEntrantForm
import json

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
                event_date = request.POST["event_date"],
                note = request.POST['note'],
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

def get_regulation_form(racetype):
    if racetype.id == 3 : #CrossCountry
        return Regulation_XC_Form
    else :
        raise ValueError(
            messages = f"未対応のRaceType { racetype.id }:{racetype.name}が検出されました。" 
        )

def get_regulation_template(racetype):
    if racetype.id == 3 : #CrossCountry
        return "race/regulations_setup_xc.html"
    else :
        raise ValueError(
            messages = f"未対応のRaceType { racetype.id }:{racetype.name}が検出されました。" 
        )


class RegulationSetupView(TemplateView):
    def get(self, request, *args, **kwargs):
        race = get_object_or_404(Race,pk=kwargs["pk"])
        template_name = get_regulation_template(race.racetype)
        context = {
                "race":race,
                "form":get_regulation_form(race.racetype)
            }       

        return render(request, template_name, context=context )

    def post(self, request, *args, **kwargs):
        race = get_object_or_404(Race,pk=kwargs["pk"])
        form = get_regulation_form(race.racetype)
        form = form(request.POST)
        
        if form.is_valid():
            race.is_regulationsetuped = True
            race.is_teamrace = form.cleaned_data.get("is_teamrace")
            
            if race.is_teamrace :
                race.team_member_count_max = form.cleaned_data.get("team_member_count_max")
                race.team_member_count_min = form.cleaned_data.get("team_member_count_min")
            else :
                race.team_member_count_max = 1
                race.team_member_count_min = 1
            
            race.is_heat =form.cleaned_data.get("is_heat")
            if race.is_heat :
                race.heat_count = form.cleaned_data.get("heat_count")
            else :
                race.heat_count = 1

            race.save()
            return redirect("race_detail", race.id)
        else:
            for err in form.errors["__all__"]:
                messages.warning(request, err)

            context = {
                "race":race,
                "form":form
            }                
            template_name = get_regulation_template(race.racetype)
            return render(request, template_name, context=context )
    
class RaceIndexView(ListView):
    model = Race
    template_name = "race/list.html"

class AddEntrantView(TemplateView):
    def get(self, request, *args, **kwargs) :
        race = get_object_or_404(Race, pk=kwargs['pk'])
        content = {
            "member_max": race.team_member_count_max,
            "member_min": race.team_member_count_min,
            "form" : AddEntrantForm,
            "object" : race
        }

        return render(request, 'race/entrant_add.html', content)

    def post(self,request, *args, **kwargs) :
        race = get_object_or_404(Race, pk=kwargs['pk'])

        form = AddEntrantForm(request.POST)
        decoder = json.JSONDecoder()
        members = decoder.decode(form.members)

        if form.is_valid() and self.members_validation(race, members) :
            pass
        else:        
            content = {
                "member_max": race.team_member_count_max,
                "member_min": race.team_member_count_min,
                "form" : form
            }

            return render(request, 'race/entrant_add.html', content)


    def members_validation(race, members):
        return False