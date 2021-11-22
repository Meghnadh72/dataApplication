from django.db import models

# Create your models here.


class Dataset(models.Model):
    column1 = models.IntegerField()
    column2 = models.IntegerField()


class DatasetName(models.Model):
    name = models.CharField(max_length=255)