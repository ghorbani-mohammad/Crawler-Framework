from django.db import models

# Create your models here.
class BaseModelAbstract(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class TelegramBot(BaseModelAbstract):
    name = models.CharField(max_length=50)
    telegram_token = models.CharField(max_length=100)

    def __str__(self):
        return f"({self.pk} - {self.name})"


class TelegramAccount(BaseModelAbstract):
    name = models.CharField(max_length=50)
    chat_id = models.CharField(max_length=10)

    def __str__(self):
        return f"({self.pk} - {self.name})"
