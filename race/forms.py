from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Category, Lap, Race, RaceType, Entrant
from place.models import Place
from django.forms.widgets import Select
import json

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

    note = forms.CharField(label="その他掲載情報", max_length=500, widget=forms.Textarea, required=False)

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

class Regulation_XC_Form(forms.Form):
    is_teamrace = forms.ChoiceField(label="チームレース", 
                            choices=[(False, "いいえ"),(True, "はい") ],
                            widget=forms.Select(attrs={"class":"form-select"}))
    teammember_count_min = forms.IntegerField(label="チーム最小人数", min_value=1, required=False, 
                            widget=forms.NumberInput(attrs={"class":"form-control"}))
    teammember_count_max = forms.IntegerField(label="チーム最大人数", min_value=1, required=False,
                            widget=forms.NumberInput(attrs={"class":"form-control"}))

    is_heat = forms.ChoiceField(label="ヒート制", 
                            choices=[(False, "いいえ"),(True, "はい") ],
                            widget=forms.Select(attrs={"class":"form-select"}))
    heat_count = forms.IntegerField(label="ヒート数", min_value=1, max_value=3, required=False, 
                            widget=forms.NumberInput(attrs={"class":"form-control"}))

    def clean_is_teamrace(self):
        select = self.cleaned_data["is_teamrace"]
        if select == "True" :
            return True
        else :
            return False 
    def clean_teammember_count_min(self):
        num = self.cleaned_data["teammember_count_min"]

        if num == None or num == 0 or num == "" :
            return 1
        else :
            return int(num)
    
    def clean_teammember_count_max(self):
        num = self.cleaned_data["teammember_count_max"]

        if num == None or num == 0 or num == "" :
            return 1
        else :
            return int(num)
    
    def clean_heat_count(self):
        num = self.cleaned_data["heat_count"]

        if num == None or num == 0 or num == "" :
            return 1
        else :
            return int(num)
    
    def clean_is_heat(self):
        select = self.cleaned_data["is_heat"]
        if select == "True" :
            return True
        else : 
            return False
    
    def clean(self):
        cleaned_data = super().clean()
        
        param = cleaned_data.get("is_teamrace")
        print( f"is_teamrace:{ param } ")

        if cleaned_data.get("is_teamrace") : 
            if cleaned_data.get("teammember_count_min") > cleaned_data.get("teammember_count_max") :
                raise ValidationError(
                    message="チームメンバーの最小人数が最大人数より多くなっています。"
                )
        return cleaned_data

class AddEntrantForm(forms.ModelForm):
    num = forms.CharField(label="ゼッケンNo", max_length=10, required=True)
    members = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean_members(self):
        membersjson = self.cleaned_data["members"]
        if membersjson == "" :
            raise ValidationError(
                message="メンバーが1名も追加されていません。"
            )

        decoder = json.JSONDecoder()
        try:
            members = decoder.decode(membersjson)
        except:
            raise ValidationError(
                message="メンバーデータが正常に取得できませんでした。"
            )
        
        race = self.instance
        members_count = len(members.keys())
        if race.team_member_count_min > members_count :
            raise ValidationError(
                message="メンバーが最少人数を満たしていません。"
            )

        if members_count > race.team_member_count_max :
            raise ValidationError(
                message="メンバーが最大人数を超えています。"
            )

        return membersjson


    class Meta():
        model = Entrant
        fields = ('team_name', 'num')


class LapEntryForm(forms.ModelForm):
    num = forms.ChoiceField(label="ゼッケンNo")

    def __init__(self, entrants=None, *args, **kwargs) :
        self.base_fields["num"].choices = [('-1', '---')] + [ (entrant["id"], entrant["num"]) for entrant in entrants ]
        super().__init__(*args, **kwargs)

    def clean_num(self):
        num = self.cleaned_data["num"]

        if not( Entrant.objects.filter(pk=num).exists() ):
            raise ValidationError(
                message="存在しないゼッケンNoです。"
            )
        
        return num

    class Meta:
        model = Lap
        fields = ("num",)
    