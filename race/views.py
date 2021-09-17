from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from .models import Category, RaceType
from place.models import Place
from account.models import Organizer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
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