from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.safestring import mark_safe
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

        if cleaned_data.get("is_teamrace") : 
            if cleaned_data.get("teammember_count_min") > cleaned_data.get("teammember_count_max") :
                raise ValidationError(
                    message="チームメンバーの最小人数が最大人数より多くなっています。"
                )
        return cleaned_data

class AddEntrantForm(forms.ModelForm):
    members = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, race=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.race = race

    def clean_num(self):
        num = self.cleaned_data["num"]
        if self.race.entrant_set.filter(num=num).exists():
            raise ValidationError(
                message=f"入力したゼッケンNo: {num} は既に使用されています。"
            )

        return num

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
        
        race = self.race
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

class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':f'list_{self._name}' })
    
    def render(self, name, value, attrs=None, renderer=None) :
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = f'<datalist id="list_{self._name}">'
        for item in self._list:
            data_list += f'<option value="{item["num"]}" data-id={item["id"]}>'
        data_list += '</datalist>'

        return mark_safe(text_html + data_list)

class LapForm(forms.ModelForm):
    num = forms.CharField(label="ゼッケンNo")

    def __init__(self, entrants=None, num_name="num", *args, **kwargs) :
        super().__init__(*args, **kwargs)
        self.fields['num'].widget = ListTextWidget(data_list=entrants, name=num_name)

    def clean_num(self):
        num = self.cleaned_data["num"]

        if not( Entrant.objects.filter(num=num).exists() ):
            raise ValidationError(
                message="存在しないゼッケンNoです。"
            )

        return num
    
    class Meta:
        model = Lap
        fields = ("num",)