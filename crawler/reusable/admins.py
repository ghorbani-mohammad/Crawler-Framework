class ReadOnlyAdminDateFieldsMIXIN:
    def __init__(self) -> None:
        self.readonly_fields = None

    base_readonly_fields = ("created_at", "updated_at", "deleted_at")

    def get_readonly_fields(self, _request, _obj=None):
        if self.readonly_fields:
            return self.readonly_fields + self.base_readonly_fields
        return self.base_readonly_fields
