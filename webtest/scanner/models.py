from django.db import models

# Create your models here.
class Report(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    file = models.CharField(max_length=50, blank=True, null=True)
    reportId = models.CharField(max_length=50, unique=True, blank=True, null=True)
    hash = models.CharField(max_length=50, unique=True, blank=True, null=True)
    stats = models.CharField(max_length=100, blank=True, null=True)