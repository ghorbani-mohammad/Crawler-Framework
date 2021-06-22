from django.contrib import admin
from reusable.other import ReadOnlyAdminDateFields

from . import models


# Register your models here.

@admin.register(models.TelegramBot)
class TelegramBotAdmin(ReadOnlyAdminDateFields, admin.ModelAdmin):
    list_display = ("pk", "name")