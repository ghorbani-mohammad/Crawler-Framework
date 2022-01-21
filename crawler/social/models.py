from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Network(BaseModel):
    name = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return f'({self.pk} - {self.name})'


class Publisher(BaseModel):
    username = models.CharField(max_length=100)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    is_channel = models.BooleanField(default=False)

    def __str__(self):
        return f'({self.pk} - {self.username})'


class Post(BaseModel):
    body = models.CharField(max_length=100)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='posts', null=True)


    def __str__(self):
        return f'({self.pk} - {self.network})'
