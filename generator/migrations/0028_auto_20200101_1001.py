# Generated by Django 2.2.7 on 2020-01-01 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0027_aoi_projaoi_projudt_udt'),
    ]

    operations = [
        migrations.AddField(
            model_name='aoi',
            name='xml',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='udt',
            name='xml',
            field=models.TextField(blank=True, null=True),
        ),
    ]
