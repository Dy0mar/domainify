# Generated by Django 2.0.7 on 2018-11-04 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0003_auto_20181104_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='telephone2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='domain',
            name='telephone3',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
