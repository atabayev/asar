# Generated by Django 2.1.2 on 2018-10-22 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grabber', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emails',
            old_name='last_emails_datetime',
            new_name='last_messages_datetime',
        ),
        migrations.AlterField(
            model_name='emails',
            name='status',
            field=models.CharField(default='1', max_length=50),
        ),
    ]
