# Generated by Django 2.2.7 on 2019-11-29 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0004_auto_20191129_0800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chassis',
            name='xml',
            field=models.TextField(blank=True, null=True),
        ),
    ]
