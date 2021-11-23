from django.db import models


class BaseModelAbstract(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Network(BaseModelAbstract):
    name = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return f'{self.pk} - {self.name}'


class Post(BaseModelAbstract):
    body = models.CharField(max_length=100)
    url = models.URLField()
    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name='posts', related_query_name='post')

    def __str__(self):
        return f'{self.pk} - <{self.network}>'
