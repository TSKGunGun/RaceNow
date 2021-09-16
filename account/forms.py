from django import forms
from django.forms import fields
from .models import User, Organizer
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}
    

class AddOrganizerForm(forms.Form):
    def __init__(self, user, *args, **kwargs ) -> None:
        super().__init__(*args, **kwargs)
        self.fields['organizer'] = forms.ChoiceField(
            choices=[ (org.id, org.name ) for org in Organizer.objects.exclude(members__in=[user])],
        )

class CreateOrganizerForm(forms.ModelForm):
    class Meta:
        model = Organizer
        fields = ("name","email_address","url")