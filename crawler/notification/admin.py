from django.contrib import admin
from reusable.admins import ReadOnlyAdminDateFieldsMIXIN

from . import models


@admin.register(models.TelegramBot)
class TelegramBotAdmin(ReadOnlyAdminDateFieldsMIXIN):
    list_display = ("pk", "name")


@admin.register(models.TelegramAccount)
class TelegramAccountAdmin(ReadOnlyAdminDateFieldsMIXIN):
    list_display = ("pk", "name", "chat_id")


@admin.register(models.MessageTemplate)
class MessageTemplateAdmin(ReadOnlyAdminDateFieldsMIXIN, admin.ModelAdmin):
    list_display = ("pk", "name", "created_at", "updated_at")


@admin.register(models.FilteringTag)
class FilteringTagAdmin(ReadOnlyAdminDateFieldsMIXIN):
    list_display = ("pk", "name")


@admin.register(models.FilteringToken)
class FilteringTokenAdmin(ReadOnlyAdminDateFieldsMIXIN):
    list_display = ("pk", "token", "tag", "created_at")
    list_filter = ("tag",)
    search_fields = ("token",)
    list_per_page = 20
