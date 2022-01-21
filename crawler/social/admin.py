from django.contrib import admin
from reusable.other import ReadOnlyAdminDateFields

from . import models


@admin.register(models.Network)
class NetworkAdmin(ReadOnlyAdminDateFields, admin.ModelAdmin):
    list_display = ("pk", "name", "url")


@admin.register(models.Publisher)
class PublisherAdmin(ReadOnlyAdminDateFields, admin.ModelAdmin):
    list_display = ("pk", "username", "network", "is_channel", "created_at")

@admin.register(models.Post)
class PostAdmin(ReadOnlyAdminDateFields, admin.ModelAdmin):
    list_display = ("pk", "publisher", "created_at")
