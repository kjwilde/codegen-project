# Generated by Django 2.2.7 on 2019-11-29 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0008_module_ischassis'),
    ]

    operations = [
        migrations.AddField(
            model_name='projchassis',
            name='name',
            field=models.CharField(default='', max_length=50),
        ),
    ]