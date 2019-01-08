from django.db import models


class Templates(models.Model):
    name = models.CharField(max_length=50, default='')
    body = models.TextField(default='')
    description = models.CharField(default='')
