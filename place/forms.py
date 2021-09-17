from django import forms
from django.core.exceptions import ValidationError
from .models import Place

class CreatePlaceForm(forms.ModelForm):
    name = forms.CharField()
    
    class Meta:
        model = Place
        fields = ("name", "address", "url")