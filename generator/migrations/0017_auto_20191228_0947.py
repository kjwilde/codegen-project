# Generated by Django 2.2.7 on 2019-12-28 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0016_projmodule_moduleid'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='points',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='module',
            name='type2',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
