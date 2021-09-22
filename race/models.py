from operator import truediv
from typing import ChainMap
from django.db import models
from account.models import Organizer
from place.models import Place

# Create your models here.
class Category(models.Model):
    name = models.CharField(verbose_name="カテゴリ名", null=False, max_length=30)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "category"

class RaceType(models.Model):
    category = models.ForeignKey(Category, verbose_name="レースカテゴリ", null=False, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="レースタイプ", null=False, max_length=30)
    
    def __str__(self) -> str:
        return f"{self.category.name} : {self.name}"

    class Meta:
        db_table = "racetype"

class RaceStatus(models.Model):
    name = models.CharField(verbose_name="ステータス",  null=False, max_length=10)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "racestatus"

class Race(models.Model):
    organizer = models.ForeignKey(Organizer, verbose_name="主催者", null=False, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, verbose_name="開催地", null=False, on_delete=models.CASCADE )
    name = models.CharField(verbose_name="レース名", null=False, max_length=50)
    url = models.URLField(verbose_name="ホームページURL", null=True, blank=True)    
    racetype = models.ForeignKey(RaceType, verbose_name="レースタイプ", null=False, on_delete=models.CASCADE)
    status = models.ForeignKey(RaceStatus, verbose_name="ステータス", null=False, default=1, on_delete=models.CASCADE)
    event_date = models.DateField("開催日", null=False)
    note = models.TextField(verbose_name="その他情報", null=True, blank=True, max_length=500 )
    
    #Regulation
    is_regulationsetuped = models.BooleanField(default=False )

    is_teamrace = models.BooleanField(verbose_name="チームレース", default=False )
    team_member_count_min = models.IntegerField(verbose_name="チーム最小人数", default=0)
    team_member_count_max = models.IntegerField(verbose_name="チームメンバー最大人数", default=0)

    is_heat = models.BooleanField(verbose_name="ヒート制", default=False)
    heat_count = models.IntegerField(verbose_name="ヒート数", default=0)

    created_at = models.DateField(verbose_name="作成日", auto_now_add=True)
    updated_at = models.DateField(verbose_name="更新日", auto_now=True)

    def __str__(self):
        return f"{self.id} : {self.organizer.name } / {self.name}"

class Entrant(models.Model):
    race = models.ForeignKey(Race, verbose_name="参加レース", null=False, on_delete=models.CASCADE)
    team_name = models.CharField(verbose_name="チーム名", max_length=60, null=True, blank=True)
    num = models.CharField(verbose_name="ゼッケンNo", max_length=10, null=True, blank=True)
    is_dns = models.BooleanField(verbose_name="DNS", default=False)
    is_dnf = models.BooleanField(verbose_name="DNF", default=False)

    def __str__(self):
        return f"{self.race.name} : {self.num}"

class Entrant_Member(models.Model):
    belonging = models.ForeignKey(Entrant, verbose_name="所属エントラント", null=False, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="エントリー名", null=False, max_length=50)

class Lap(models.Model):
    race = models.ForeignKey(Race, verbose_name="レース", null=False, on_delete=models.CASCADE)
    entrant = models.ForeignKey(Entrant, verbose_name="エントラント", null=False, on_delete=models.CASCADE)
    laptime = models.TimeField(verbose_name="ラップタイム", null=True)