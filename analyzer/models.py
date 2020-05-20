from django.db import models

# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()

    class Meta:
        abstract = True


class News(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=70)
    source = models.CharField(max_length=70)
    agency_id = models.BigIntegerField()
    class Meta:
       managed = False
       db_table = 'news'
    
    def __str__(self):
        return '{}. {}'.format(self.id, self.title)

class Operation(BaseModel):
    news_id = models.ForeignKey('News', related_name='operations', related_query_name='operation',
                                 on_delete=models.CASCADE)
    keyword = models.BooleanField(default=False)
    ner = models.BooleanField(default=False)
    category = models.BooleanField(default=False)
    sentiment = models.BooleanField(default=False)
    doc2vec = models.BooleanField(default=False)
    related_news = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.id)


class Option(models.Model):
    key = models.CharField(max_length=70)
    value = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       managed = False
       db_table = 'options'
    
    def __str__(self):
        return '{}'.format(self.key)    