from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, DetailView
from .forms import CustomUserCreationForm
from .models import Organizer, User

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