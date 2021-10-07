from django.core.checks import messages
from django.core.exceptions import PermissionDenied
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_GET, require_POST
from .models import Entrant, Entrant_Member, Race, RaceStatus, RaceType,Lap
from place.models import Place
from account.models import Organizer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import CreateRaceForm, Regulation_XC_Form, AddEntrantForm, LapForm
from django.db import transaction
import json
import pytz

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

        context["IsMember"] = self.object.is_member(self.request.user)
        context["Is_CanChangeRegulation"] = self.object.status.id < RaceStatus.RACE_STATUS_ENTRY
        context["Is_Entry"] = self.object.status.id == RaceStatus.RACE_STATUS_ENTRY
        
        context["Is_canstart"] = (self.object.status.id == RaceStatus.RACE_STATUS_ENTRY and self.object.entrant_set.all().exists() )
        
        context["Is_RaceHold"] = (self.object.status.id == RaceStatus.RACE_STATUS_HOLD)
        
        context["Is_ShowResult"] = (self.object.status.id >= RaceStatus.RACE_STATUS_HOLD)
        
        context["entrants"] = self.object.entrant_set.all()[:3]
        context["result"] = Race.objects.get_result(self.object.id)[:3]
        
        context["place"] = self.object.place
        
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

@method_decorator(login_required, name='dispatch')
class RegulationSetupView(TemplateView):
    def get(self, request, *args, **kwargs):
        race = get_object_or_404(Race,pk=kwargs["pk"])
        if not race.is_member(request.user) :
            raise PermissionDenied

        if race.status.id != RaceStatus.RACE_STATUS_DEFAULT :
            raise PermissionDenied
        
        template_name = get_regulation_template(race.racetype)
        context = {
                "race":race,
                "form":get_regulation_form(race.racetype)
            }       

        return render(request, template_name, context=context )

    def post(self, request, *args, **kwargs):
        race = get_object_or_404(Race,pk=kwargs["pk"])
        if not race.is_member(request.user) :
            raise PermissionDenied

        if race.status.id != RaceStatus.RACE_STATUS_DEFAULT :
            raise PermissionDenied

        form = get_regulation_form(race.racetype)
        form = form(request.POST)
        
        if form.is_valid():
            race.is_regulationsetuped = True
            race.is_teamrace = form.cleaned_data.get("is_teamrace")
            
            if race.is_teamrace :
                race.team_member_count_max = form.cleaned_data.get("teammember_count_max")
                race.team_member_count_min = form.cleaned_data.get("teammember_count_min")
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
    
@method_decorator(login_required, name='dispatch')
class AddEntrantView(TemplateView):
    def get(self, request, *args, **kwargs) :
        race = get_object_or_404(Race, pk=kwargs['pk'])
        if not race.is_member(request.user) :
            raise PermissionDenied
        
        content = {
            "member_max": race.team_member_count_max,
            "member_min": race.team_member_count_min,
            "form" : AddEntrantForm,
            "object" : race
        }

        return render(request, 'race/entrant_add.html', content)

    def post(self,request, *args, **kwargs) :
        race = get_object_or_404(Race, pk=kwargs['pk'])
        if not race.is_member(request.user) :
            raise PermissionDenied

        form = AddEntrantForm(race=race, data=request.POST)
        if form.is_valid() :
            decoder = json.JSONDecoder()
            members = decoder.decode(request.POST["members"])

            with transaction.atomic():
                entrant = Entrant(
                    race = race,
                    team_name = form.cleaned_data.get("team_name"),
                    num = form.cleaned_data.get("num")
                )
                entrant.save()
                
                for v in members.values():
                    member = Entrant_Member.objects.create(
                        belonging = entrant,
                        name = v["name"]
                    )

            return redirect('race_detail', race.id)
        
        #memberは関連Inputがないのでフラッシュメッセージで出力
        for err in form.errors['members'] :
            messages.error(request, err)

        content = {
            "member_max": race.team_member_count_max,
            "member_min": race.team_member_count_min,
            "form" : form,
            "object" : race
        }

        return render(request, 'race/entrant_add.html', content)

@require_POST
@login_required
def fixedRegulation(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied

    race.status = RaceStatus.objects.get(pk=RaceStatus.RACE_STATUS_ENTRY)
    race.save()

    return redirect('race_detail', race.id)

@require_POST
@login_required
def startRace(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied

    race.status = RaceStatus.objects.get(pk=RaceStatus.RACE_STATUS_HOLD)
    race.save()

    return redirect('race_detail', race.id)

@require_GET
@login_required
def inputResult(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied

    return render(request, "race/input_result.html", get_context_resultinput(race.id))

@require_POST
@login_required
def addLap(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied
    
    form = get_lap_form(race.id, data=request.POST, instance=race)
    if form.is_valid():
        entrant = get_object_or_404(Entrant, num=request.POST["num"])    
        Lap.objects.create(
            entrant = entrant
        )
        return redirect('input_result', pk=race.id)

    return render(request, "race/input_result.html", get_context_resultinput(race.id))
    

@require_POST
@login_required
def deleteLap(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied
    
    form = get_lap_form(race.id, data=request.POST, instance=race)

    if form.is_valid():
        entrant = get_object_or_404(Entrant, num=request.POST["num"])    
        if not( entrant.lap_set.all().exists() ):
            return redirect('input_result', pk=race.id)
            
        lap = entrant.lap_set.order_by('-created_at').first()
        lap.delete()

        return redirect('input_result', pk=race.id)

    return render(request, "race/input_result.html", get_context_resultinput(race.id))
    
def get_context_resultinput(raceid):
    race = get_object_or_404(Race, pk=raceid)
    context = {
        "object":race,
        "result":Race.objects.get_result(race.id),
        "lap_entry_form" : get_lap_form(race.id)
    }

    return context

def get_lap_form(raceid, *args, **kwargs):
    race = get_object_or_404(Race, pk=raceid)

    nums = []
    for entrant in race.entrant_set.all():
        nums.append({"id": entrant.id, "num":entrant.num})

    return LapForm(entrants=nums, *args, **kwargs)

@require_GET
def get_entrant_info(request, *args, **kwargs):
    entrant = get_object_or_404(Entrant, pk=kwargs["pk"])

    data = {
        "team_name" : entrant.team_name,
        "member" : [ member.name for member in entrant.entrant_member_set.all() ],
        "laps" : get_lap_info(entrant)
    }

    return JsonResponse(data)

def get_lap_info(entrant):
    laps = {}
    count = 1
    tz = pytz.timezone('Asia/Tokyo')
    for lap in entrant.lap_set.all().order_by("created_at"):
        laps[str(count)] = { "input_time" : lap.created_at.astimezone(tz).strftime("%Y/%m/%d %H:%M:%S") }
        count += 1
    
    return laps

@require_GET
def showResult(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if race.status.id == RaceStatus.RACE_STATUS_HOLD or race.status.id == RaceStatus.RACE_STATUS_END :
        return render(request, "race/race_result.html", get_context_resultinput(pk))
    else :
        return render(request, "race/result_notshow.html", get_context_resultinput(pk))