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
from django.utils import timezone
from .forms import CreateRaceForm, Regulation_XC_Form, EditEntrantForm, LapForm,EntrantCSVUploadForm
from django.db import transaction
from datetime import datetime
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
        context["Is_ShowEntrants"] = self.object.status.id >= RaceStatus.RACE_STATUS_ENTRY
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
            "form" : EditEntrantForm,
            "object" : race
        }

        return render(request, 'race/entrant_add.html', content)

    def post(self,request, *args, **kwargs) :
        race = get_object_or_404(Race, pk=kwargs['pk'])
        if not race.is_member(request.user) :
            raise PermissionDenied

        form = EditEntrantForm(race=race, data=request.POST)
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
            
            messages.success(request, f"ゼッケンNo {entrant.num}のエントラントを追加しました。")

            return redirect('entrant_index', race.id)
        
        content = {
            "member_max": race.team_member_count_max,
            "member_min": race.team_member_count_min,
            "form" : form,
            "object" : race
        }

        #memberは関連InputがHiddenなので一旦配列に格納しておく
        if "members" in form.errors.keys():
            members_error = []
            for err in form.errors['members'] :
                members_error.append(err)

            content["members_error"] = members_error
        
        return render(request, 'race/entrant_add.html', content)

@method_decorator(login_required, name='dispatch')
class EditEntrantView(AddEntrantView):
    def get(self, request, *args, **kwargs) :
        race = get_object_or_404(Race, pk=kwargs['pk'])
        if not race.is_member(request.user) :
            raise PermissionDenied
        
        entrant = get_object_or_404(Entrant, pk=kwargs['ent_pk'])
        form = EditEntrantForm(instance=entrant)
        content = {
            "member_max": race.team_member_count_max,
            "member_min": race.team_member_count_min,
            "form" : form,
            "object" : race,
            "entrant" : entrant
        }

        return render(request, 'race/entrant_edit.html', content)
    
    
    def post(self,request, *args, **kwargs) :
        race = get_object_or_404(Race, pk=kwargs['pk'])
        entrant = get_object_or_404(Entrant, pk=kwargs['ent_pk'])
        if not race.is_member(request.user) :
            raise PermissionDenied

        form = EditEntrantForm(race=race, data=request.POST, instance=entrant)
        if form.is_valid() :
            decoder = json.JSONDecoder()
            members = decoder.decode(request.POST["members"])
            
            with transaction.atomic():
                Entrant_Member.objects.filter(belonging=entrant).delete()
                entrant.team_name = form.cleaned_data.get("team_name")
                entrant.num = form.cleaned_data.get("num")
                entrant.save()
                
                for v in members.values():
                    member = Entrant_Member.objects.create(
                        belonging = entrant,
                        name = v["name"]
                    )

            messages.success(request, f"ゼッケンNo {entrant.num}のエントラントの情報を更新しました。")

            return redirect('entrant_index', race.id)
        
        content = {
            "member_max": race.team_member_count_max,
            "member_min": race.team_member_count_min,
            "form" : form,
            "object" : race,
            "entrant" : entrant
        }

        #memberは関連InputがHiddenなので一旦配列に格納しておく
        if "members" in form.errors.keys():
            members_error = []
            for err in form.errors['members'] :
                members_error.append(err)

            content["members_error"] = members_error
        
        return render(request, 'race/entrant_edit.html', content)

@require_POST
@login_required
def deleteEntrant(request, pk, ent_pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied

    entrant = get_object_or_404(Entrant, pk=ent_pk)

    num = entrant.num
    entrant.delete()

    messages.success(request, f"ゼッケンNo:{num}のエントラントの削除が完了しました。")

    return redirect('entrant_index', race.id)

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
def finishRace(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied

    race.status = RaceStatus.objects.get(pk=RaceStatus.RACE_STATUS_END)
    race.save()

    return redirect('race_detail', race.id)

@require_POST
@login_required
def startRace(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied

    race.status = RaceStatus.objects.get(pk=RaceStatus.RACE_STATUS_HOLD)
    race.start_at = timezone.now()
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
        entrant = get_object_or_404(Entrant, race=race, num=request.POST["num"])    
        
        laptime = None
        if entrant.lap_set.all().exists() :
            laptime = getLaptime(entrant.lap_set.order_by('created_at').reverse().first().created_at)
        else:
            laptime = getLaptime(entrant.race.start_at)
        
        Lap.objects.create(
            entrant = entrant,
            laptime = laptime
        )
        messages.success(request, f"ゼッケンNo:{request.POST['num']}にラップを追加しました。")
        return redirect('input_result', pk=race.id)

    for msgs in form.errors.values():
        for msg in msgs :
            messages.error(request, f"エラーのため、ラップ追加に失敗しました。{msg}")

    return redirect('input_result', pk=race.id)

def getLaptime(lastTime):
    td = abs(timezone.now() - lastTime)
    return (datetime(1,1,1,0,0,0) + td).time()

@require_POST
@login_required
def deleteLap(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied
    
    form = get_lap_form(race.id, data=request.POST, instance=race)

    if form.is_valid():
        entrant = get_object_or_404(Entrant, race=race, num=request.POST["num"])    
        if not( entrant.lap_set.all().exists() ):
            return redirect('input_result', pk=race.id)
            
        lap = entrant.lap_set.order_by('-created_at').first()
        lap.delete()

        messages.success(request, f"ゼッケンNo:{request.POST['num']}の最後のラップを削除しました。")
        return redirect('input_result', pk=race.id)

    for msgs in form.errors.values():
        for msg in msgs :
            messages.error(request, f"エラーのため、ラップ削除に失敗しました。{msg}")

    return redirect('input_result', pk=race.id)
    
def get_context_resultinput(raceid):
    race = get_object_or_404(Race, pk=raceid)
    context = {
        "object":race,
        "result":Race.objects.get_result(race.id),
        "lap_entry_form" : get_lap_form(race.id),
        "set_dnf_form" : get_setdnf_form(race.id),
        "unset_dnf_form" : get_unsetdnf_form(race.id),
    }

    return context

def get_lap_form(raceid, *args, **kwargs):
    race = get_object_or_404(Race, pk=raceid)

    nums = []
    for entrant in race.entrant_set.all():
        nums.append({"id": entrant.id, "num":entrant.num})

    return LapForm(entrants=nums, *args, **kwargs)


def get_setdnf_form(raceid, *args, **kwargs):
    race = get_object_or_404(Race, pk=raceid)

    nums = []
    for entrant in race.entrant_set.filter(is_dnf=False).all():
        nums.append({"id": entrant.id, "num":entrant.num})

    return LapForm(entrants=nums, num_name="setdnf_num", *args, **kwargs)


def get_unsetdnf_form(raceid, *args, **kwargs):
    race = get_object_or_404(Race, pk=raceid)

    nums = []
    for entrant in race.entrant_set.filter(is_dnf=True).all():
        nums.append({"id": entrant.id, "num":entrant.num})

    return LapForm(entrants=nums, num_name="unsetdnf_num", *args, **kwargs)

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
        laps[str(count)] = { 
            "input_time" : lap.created_at.astimezone(tz).strftime("%Y/%m/%d %H:%M:%S"), 
            "lap_time" : lap.laptime.strftime("%H:%M:%S") 
        }
        count += 1
    
    return laps

@require_GET
def showResult(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if race.status.id == RaceStatus.RACE_STATUS_HOLD or race.status.id == RaceStatus.RACE_STATUS_END :
        return render(request, "race/race_result.html", get_context_resultinput(pk))
    else :
        return render(request, "race/result_notshow.html", get_context_resultinput(pk))

@require_POST
@login_required
def setDNF(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied
    
    form = get_lap_form(race.id, data=request.POST, instance=race)

    if form.is_valid():
        entrant = get_object_or_404(Entrant, race=race, num=request.POST["num"])    
        entrant.is_dnf = True
        entrant.save()    
        
        messages.success(request, f"ゼッケンNo:{request.POST['num']}をDNFに設定しました。")
        return redirect('input_result', pk=race.id)

    for msgs in form.errors.values():
        for msg in msgs :
            messages.error(request, f"エラーのため、DNF設定に失敗しました。{msg}")

    return redirect('input_result', pk=race.id)

@require_POST
@login_required
def unsetDNF(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied
    
    form = get_lap_form(race.id, data=request.POST, instance=race)

    if form.is_valid():
        entrant = get_object_or_404(Entrant, race=race, num=request.POST["num"])    
        entrant.is_dnf = False
        entrant.save()    
        
        messages.success(request, f"ゼッケンNo:{request.POST['num']}のDNF設定を解除しました。")
        return redirect('input_result', pk=race.id)

    for msgs in form.errors.values():
        for msg in msgs :
            messages.error(request, f"エラーのため、DNF設定解除に失敗しました。{msg}")

    return redirect('input_result', pk=race.id)

class EntrantIndexView(ListView):
    model = Entrant
    
    def get_context_data(self, **kwargs):
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context["race"] = race
        context["csvuploadForm"] = EntrantCSVUploadForm
        context["IsMember"] = race.is_member(self.request.user)
        context["Is_Entry"] = race.status.id == RaceStatus.RACE_STATUS_ENTRY
        return context

    def get_queryset(self, **kwargs):
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        qs = super().get_queryset().filter(race=race)
        return qs

@login_required
@require_POST
def uploadEntrantCSVFile(request, pk):    
    race = get_object_or_404(Race, pk=pk)
    if not race.is_member(request.user) :
        raise PermissionDenied
    
    form = EntrantCSVUploadForm(race=race, data=request.POST, files=request.FILES)

    if form.is_valid():
        csv_data = form.cleaned_data["file"]
        with transaction.atomic():
            for line in csv_data:
                if not Entrant.objects.filter(race=race).filter(num=line[0]).exists():
                    ent = Entrant.objects.create(
                        race = race,
                        num = line[0],
                        team_name = line[1]
                    )

                else :
                    ent = get_object_or_404(Entrant, race=race, num=line[0])
                    ent.team_name = line[1]
                    ent.save()
                    Entrant_Member.objects.filter(belonging=ent).delete()
                                        
                for member in line[2].split(','):
                    Entrant_Member.objects.create(
                        belonging = ent,
                        name = member
                    )
        messages.success(request, "CSV取り込みが完了しました。")
        return redirect('entrant_index', pk=pk)

    for msgs in form.errors.values():
        for msg in msgs :
            messages.error(request, f"CSV取り込みでエラーが発生しました。{msg}")

    return redirect('entrant_index', pk=pk)