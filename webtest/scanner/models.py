from django.db import models

# Create your models here.
class Report(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    fileName = models.CharField(max_length=100, blank=True, null=True)
    fileId = models.CharField(max_length=100, unique=True, blank=True, null=True)
    SHA_256 = models.CharField(max_length=100, unique=True, blank=True, null=True)
    stats = models.CharField(max_length=100, blank=True, null=True)
    modifiedAt = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.fileName
