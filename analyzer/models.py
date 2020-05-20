from django.db import models

# Create your models here.
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