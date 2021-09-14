from django import forms
from .models import User, Organizer
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}
    

