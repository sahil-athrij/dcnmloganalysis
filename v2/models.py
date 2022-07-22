from django.db import models


# Create your models here.

class SR(models.Model):
    sr_number = models.IntegerField(primary_key=True)


class SRFiles(models.Model):
    sr_number = models.ForeignKey(SR, on_delete=models.CASCADE, related_name='files')
    fileId = models.CharField(max_length=200)
    fileName = models.CharField(max_length=200)
    fileContentType = models.CharField(max_length=200)
