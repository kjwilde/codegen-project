# Generated by Django 2.2.7 on 2019-12-28 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0022_auto_20191228_1014'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleCatagory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catagory', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='ModuleType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=25)),
            ],
        ),
        migrations.AddField(
            model_name='module',
            name='catagory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='generator.ModuleCatagory'),
        ),
        migrations.AddField(
            model_name='module',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='generator.ModuleType'),
        ),
    ]