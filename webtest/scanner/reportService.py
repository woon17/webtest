from django.utils import timezone
from .models import Report

def updateReport(stats, fileName, fileId, SHA_256):
    reportObj=Report.objects.filter(SHA_256=SHA_256)[0]
    reportObj.stats=stats,
    reportObj.fileName=fileName,
    reportObj.fileId=fileId,
    reportObj.modifiedAt=timezone.localtime(timezone.now())
    reportObj.save()

def createReport(stats, fileName, fileId, SHA_256):
    Report.objects.create(
        fileId=fileId,
        stats=stats,
        SHA_256=SHA_256,
        fileName=fileName,
    )
