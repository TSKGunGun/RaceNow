from django.shortcuts import render
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

# Create your views here.
class CreateUserView(CreateView):
    template_name = "account/create_user.html"
    form_class = CustomUserCreationForm