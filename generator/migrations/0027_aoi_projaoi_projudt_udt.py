# Generated by Django 2.2.7 on 2020-01-01 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0026_projmodule_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='AOI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('versionMajor', models.IntegerField()),
                ('versionMinor', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UDT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('versionMajor', models.IntegerField()),
                ('versionMinor', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ProjUDT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='generator.Project')),
                ('udtId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='generator.UDT')),
            ],
        ),
        migrations.CreateModel(
            name='ProjAOI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aoiId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='generator.AOI')),
                ('projId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='generator.Project')),
            ],
        ),
    ]
