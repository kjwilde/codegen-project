# Generated by Django 2.2.7 on 2019-11-29 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0005_auto_20191129_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='slots',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='xml',
            field=models.TextField(blank=True, null=True),
        ),
    ]