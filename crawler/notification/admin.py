from django.contrib import admin
from reusable.admins import ReadOnlyAdminDateFields

from . import models


@admin.register(models.TelegramBot)
class TelegramBotAdmin(ReadOnlyAdminDateFields, admin.ModelAdmin):
    list_display = ("pk", "name")


@admin.register(models.TelegramAccount)
class TelegramAccountAdmin(ReadOnlyAdminDateFields, admin.ModelAdmin):
    list_display = ("pk", "name", "chat_id")
