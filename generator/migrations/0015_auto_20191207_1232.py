# Generated by Django 2.2.7 on 2019-12-07 18:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0014_auto_20191207_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projmodule',
            name='chassisId',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='generator.ProjChassis'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='projmodule',
            name='projId',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='generator.Project'),
        ),
    ]
