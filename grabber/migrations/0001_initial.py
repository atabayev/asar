# Generated by Django 2.1.2 on 2018-10-22 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Emails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(default='', max_length=50)),
                ('password', models.CharField(default='', max_length=50)),
                ('last_scan_datetime', models.CharField(default='', max_length=20)),
                ('last_emails_datetime', models.CharField(default='', max_length=50)),
                ('status', models.CharField(default='', max_length=50)),
            ],
        ),
    ]
