from django.shortcuts import render
from django.views.generic import TemplateView
from race.models import Race

# Create your views here.
class IndexView(TemplateView):
    template_name = "index/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["new_arrivals"] = Race.objects.order_by('created_at').reverse()[:3]

        return context