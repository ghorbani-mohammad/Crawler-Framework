from django.contrib import admin


class ReadOnlyAdminDateFieldsMIXIN(admin.ModelAdmin):
    """
    This mixin is used to make common date fields as
    readonly fields.
    """

    base_readonly_fields = ("created_at", "updated_at", "deleted_at")

    def get_readonly_fields(self, _request, _obj=None):
        """
        Returns the read-only fields.

        :param _request: A request object.
        :param _obj: An optional object instance.
        :return: A list of read-only fields.
        """
        readonly_fields = getattr(self, "readonly_fields")
        if readonly_fields:
            return readonly_fields + self.base_readonly_fields
        return self.base_readonly_fields
