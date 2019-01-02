# Generated by Django 2.0.7 on 2018-11-04 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0002_auto_20181020_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionlog',
            name='action',
            field=models.CharField(choices=[('ADD_DOMAIN', 'ADD_DOMAIN'), ('EDIT_DOMAIN', 'EDIT DOMAIN'), ('DELETE_DOMAIN', 'DELETE DOMAIN'), ('LOGIN', 'LOGIN')], max_length=255),
        ),
        migrations.AlterField(
            model_name='domain',
            name='pci_scan',
            field=models.BooleanField(default=False),
        ),
    ]