# Generated by Django 2.0.7 on 2019-03-13 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('id',), 'permissions': (('managers', 'Can get access to advanced functional'),)},
        ),
    ]
