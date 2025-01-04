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


@admin.register(models.FilteringTag)
class FilteringTagAdmin(ReadOnlyAdminDateFieldsMIXIN, admin.ModelAdmin):
    list_display = ("pk", "name")


@admin.register(models.FilteringToken)
class FilteringTokenAdmin(ReadOnlyAdminDateFieldsMIXIN, admin.ModelAdmin):
    list_display = ("pk", "token", "tag")
    list_filter = ("tag",)
    search_fields = ("token",)
