from chunked_upload.models import ChunkedUpload

# 'ChunkedUpload' class provides almost everything for you.
# if you need to tweak it little further, create a model class
# by inheriting "chunked_upload.models.AbstractChunkedUpload" class
from django.db import models


class Display(models.Model):
    id = models.IntegerField(primary_key=True)
    html = models.CharField(max_length=100000)
