# Generated by Django 2.0.13 on 2019-04-16 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0008_auto_20190322_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='redirect_phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
