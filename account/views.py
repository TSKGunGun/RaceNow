from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse
from django.utils import translation
from django.views.generic import CreateView, TemplateView, DetailView
from .forms import CustomUserCreationForm, AddOrganizerForm, CreateOrganizerForm
from .models import Organizer, User
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.db import transaction

# Create your views here.
class CreateUserView(CreateView):
    model = User
    template_name = "account/create_user.html"
    form_class = CustomUserCreationForm
    success_url = "/"

class UserDetailView(DetailView):
    model = User
    template_name = "account/user_detail.html"
    login_required = True

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context["AddOrgForm"] = AddOrganizerForm(user=self.request.user)

        return context

@require_POST
@login_required
def delete_organizer_member(request):
    org_id = request.POST['organizer']
    org = get_object_or_404(Organizer, pk=org_id)
    user = request.user
    
    if org.owner == user :
        raise ValidationError(
            message="レース主催団体のオーナーはメンバーから削除できません。"
        )
    else :
        org.members.remove(user)

    return redirect( f'/account/{ user.pk }/detail' )

@require_POST
@login_required
def add_organizer_member(request):
    org_id = request.POST['organizer']
    org = get_object_or_404(Organizer, pk=org_id)

    user = request.user

    if (org.owner != user) and (org.members.filter(pk=user.id).count() == 0 ) :
        org.members.add(user)
        return redirect( f'/account/{ user.pk }/detail' )
    else :
        return redirect( f'/account/{ user.pk }/detail' )

class CreateOrganizerView(CreateView):
    model = Organizer
    login_required = True
    template_name = 'organizer/create.html'
    form_class = CreateOrganizerForm

    def post(self, request):
        form = self.get_form()
        org = Organizer(
                owner = self.request.user,
                name = request.POST['name'],
                email_address = request.POST['email_address'],
                url = request.POST['url']
        )
        self.object = org
        if form.is_valid() :
            with transaction.atomic() :
                org.save()
                org.members.add(self.request.user)

            return redirect('organizer_detail', pk=org.id)
        else:
            return self.form_invalid(form)

    def get_success_url(self) -> str:
        return reverse('organizer_detail', kwargs={'pk':self.object.id})

class OrganizerDetailView(DetailView):
    model = Organizer
    login_required = False
    template_name = 'organizer/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["races"] = self.object.race_set.all()[:5]

        return context