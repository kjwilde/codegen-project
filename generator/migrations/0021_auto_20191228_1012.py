# Generated by Django 2.2.7 on 2019-12-28 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0020_auto_20191228_1009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='catagory',
        ),
        migrations.RemoveField(
            model_name='module',
            name='type',
        ),
    ]