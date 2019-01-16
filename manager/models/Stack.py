from django.db import models


class Stack(models.Model):
    sender = models.CharField(max_length=50, default='')
    sender_password = models.CharField(max_length=50, default='')
    email = models.CharField(max_length=50, null=False)
    password = models.CharField(max_length=10, default='')
    subject = models.CharField(max_length=50, default='')
    body = models.TextField(default='')
    country = models.CharField(max_length=50, default='unknown')
    description = models.TextField(default='')
    method = models.CharField(max_length=1, default='')
    by_virus = models.CharField(max_length=1, default='')
    by_fishing = models.CharField(max_length=1, default='')
    date_add = models.CharField(max_length=20, default='')
    date_hacked = models.CharField(max_length=20, default='')
    comment = models.TextField(default='')
    status = models.CharField(max_length=1, default='0')
    who_hacked = models.CharField(max_length=20, default='')
    deleted = models.CharField(max_length=1, default='')
    ftp_host = models.CharField(max_length=50, default='')
    ftp_login = models.CharField(max_length=50, default='')
    ftp_password = models.CharField(max_length=50, default='')
