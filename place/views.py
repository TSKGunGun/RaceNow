from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls.base import reverse
from django.views.generic import CreateView,DetailView
from .forms import CreatePlaceForm
from .models import Place

# Create your views here.
@method_decorator(login_required, name='dispatch')
class CreatePlaceView(CreateView):
    model = Place
    template_name = "place/create.html"
    form_class = CreatePlaceForm

    def post(self, request, *args: str, **kwargs) :
        place = Place(
            name = request.POST["name"],
            address = request.POST["address"],
            url = request.POST["url"]
        )
        self.object = place
        form = self.get_form()
        if form.is_valid():
            place.owner = request.user
            place.save()
            return redirect("place_detail", pk=place.id)
        else:
            return self.form_invalid(form)

    def get_success_url(self) -> str:
        return reverse('place_detail', {"pk":self.object.id})

class PlaceDetailView(DetailView):
    model = Place
    template_name = "place/detail.html"