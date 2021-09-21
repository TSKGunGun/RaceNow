from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Category, Race, RaceType
from place.models import Place
from django.forms.widgets import Select


class RaceTypeSelect(Select):
    def __init__(self, attrs=None, choices=(), queryset=None):
        self.queryset = queryset
        super().__init__(attrs, choices)
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value and value != -1:
            racetype = self.queryset.get(pk=value)
            option['attrs'].update({'parent_id' : racetype.category.id})
        return option

def EventDateValidator(value):
    if timezone.now().today().date() > value:
        raise ValidationError(
            message="開催日に過去の日付は設定できません。"
        )

class CreateRaceForm(forms.ModelForm):
    place = forms.ChoiceField(label="レース開催地",
        choices= lambda: [(-1, '---' )] + [( item.id, item.name) for item in Place.objects.all()]
    )
    
    event_date = forms.DateField(label="開催日", widget=AdminDateWidget(), validators=[EventDateValidator],)

    category = forms.ChoiceField(label="レースカテゴリ",
        choices= lambda: [(-1, '---' )] + [( item.id, item.name) for item in Category.objects.all()]
    )

    racetype = forms.ChoiceField(label="レースタイプ",
        choices= lambda: [(-1, '---' )]+ [( item.id, item.name) for item in RaceType.objects.all()],
        widget=RaceTypeSelect(attrs={"disabled":"true"}, queryset=RaceType.objects.all())
    )

    url = forms.URLField(label="ホームページURL", required=False)

    def clean_place(self):
        place = self.cleaned_data['place']
        return int(place)

    def clean_category(self):
        category = self.cleaned_data['category']
        return int(category)
    
    def clean_racetype(self):
        racetype = self.cleaned_data['racetype']
        return int(racetype)

    class Meta:
        model = Race
        fields = ("name",)
