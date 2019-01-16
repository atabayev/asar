from django.db import models


class Emails(models.Model):
    email = models.CharField(max_length=50, unique=True, default='')
    password = models.CharField(max_length=50, default='')
    last_scan_datetime = models.CharField(max_length=20, default='')
    last_messages_datetime = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='1')
    description = models.TextField(default='')
    comment = models.TextField(default=' ', null=True)


class Zips(models.Model):
    name = models.CharField(max_length=100, default='')
    path = models.CharField(max_length=200, default='')
