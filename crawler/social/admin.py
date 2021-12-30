from django.contrib import admin
from reusable.other import ReadOnlyAdminDateFields

from . import models


@admin.register(models.Network)
class NetworkAdmin(ReadOnlyAdminDateFields, admin.ModelAdmin):
    list_display = ("pk", "name", "url")
