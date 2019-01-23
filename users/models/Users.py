from django.db import models


class Users(models.Model):
    username = models.CharField(max_length=10, unique=True, null=False)
    password = models.CharField(max_length=100, default='')
    token = models.CharField(max_length=40, default='')
    atk_cnt_vir = models.CharField(max_length=6, default='')
    atk_cnt_fish = models.CharField(max_length=6, default='')
    hckd_cnt_vir = models.CharField(max_length=6, default='')
    hckd_cnt_fish = models.CharField(max_length=6, default='')
    last_atk_date = models.CharField(max_length=20, default='')
    log_file = models.CharField(max_length=150, default='')
    status = models.CharField(max_length=1, default='0')

