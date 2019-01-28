from django.db import models


class Configs(models.Model):
    name = models.CharField(max_length=50, default='')
    value = models.CharField(max_length=50, default='')


class VpnFiles(models.Model):
    name = models.CharField(max_length=50, default='')
    path = models.CharField(max_length=200, default='')
