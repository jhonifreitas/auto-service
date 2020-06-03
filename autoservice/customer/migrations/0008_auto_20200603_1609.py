# Generated by Django 2.2.10 on 2020-06-03 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_auto_20200603_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='lat',
            field=models.FloatField(default=0, max_length=255, verbose_name='Latitude'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='lng',
            field=models.FloatField(default=0, max_length=255, verbose_name='Longitude'),
            preserve_default=False,
        ),
    ]
