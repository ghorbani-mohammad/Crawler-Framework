from django.db import models

from reusable.models import BaseModel


class TelegramBot(BaseModel):
    name = models.CharField(max_length=50)
    telegram_token = models.CharField(max_length=100)

    def __str__(self):
        return f"({self.pk} - {self.name})"


class TelegramAccount(BaseModel):
    name = models.CharField(max_length=50)
    chat_id = models.CharField(max_length=10)

    def __str__(self):
        return f"({self.pk} - {self.name})"


class MessageTemplate(BaseModel):
    name = models.CharField(max_length=50)
    text = models.TextField()

    def __str__(self):
        return f"({self.pk} - {self.name})"


class FilteringTag(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"({self.pk} - {self.name})"


class FilteringToken(BaseModel):
    token = models.CharField(max_length=50)
    tag = models.ForeignKey(FilteringTag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["token", "tag"]

    def __str__(self):
        return f"({self.pk} - {self.token})"
