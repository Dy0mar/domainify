# Generated by Django 2.0.13 on 2019-03-17 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190314_1419'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('id',), 'permissions': (('supermanagers', 'Can get access to advanced functional'), ('can_manage_alexa_traffic', 'Can manage Alexa traffic'), ('can_manage_domain_registrar', 'Can manage Domain Name Registrar'), ('can_edit_site', 'Can edit site'))},
        ),
    ]