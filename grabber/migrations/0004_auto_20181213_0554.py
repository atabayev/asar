# Generated by Django 2.1.4 on 2018-12-13 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grabber', '0003_emails_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emails',
            name='comment',
            field=models.CharField(default=' ', max_length=100, null=True),
        ),
    ]
