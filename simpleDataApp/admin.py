from django.contrib import admin
from .models import DatasetName, Dataset

# Register your models here.

admin.site.register(Dataset)
admin.site.register(DatasetName)

