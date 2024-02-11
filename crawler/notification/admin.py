from django.contrib import admin
from reusable.admins import ReadOnlyAdminDateFieldsMIXIN

from . import models


@admin.register(models.TelegramBot)
class TelegramBotAdmin(ReadOnlyAdminDateFieldsMIXIN, admin.ModelAdmin):
    list_display = ("pk", "name")


@admin.register(models.TelegramAccount)
class TelegramAccountAdmin(ReadOnlyAdminDateFieldsMIXIN, admin.ModelAdmin):
    list_display = ("pk", "name", "chat_id")

@admin.register(models.MessageTemplate)
class MessageTemplateAdmin(ReadOnlyAdminDateFieldsMIXIN, admin.ModelAdmin):
    list_display = ("pk", "name", "created_at", "updated_at")
