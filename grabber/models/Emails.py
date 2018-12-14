from django.db import models


class Emails(models.Model):
    email = models.CharField(max_length=50, default='')
    password = models.CharField(max_length=50, default='')
    last_scan_datetime = models.CharField(max_length=20, default='')
    last_messages_datetime = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='1')
    comment = models.CharField(max_length=100, default=' ', null=True)
