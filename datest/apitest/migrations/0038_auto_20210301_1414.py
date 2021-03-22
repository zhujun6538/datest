# Generated by Django 3.1.7 on 2021-03-01 06:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0037_testreport_errors'),
    ]

    operations = [
        migrations.CreateModel(
            name='CALLFUNC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
            ],
            options={
                'verbose_name_plural': 'call调用方法',
            },
        ),
        migrations.AlterModelOptions(
            name='func',
            options={'verbose_name_plural': 'setup调用方法'},
        ),
        migrations.AddField(
            model_name='testcase',
            name='callfunc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.callfunc'),
        ),
        migrations.AddField(
            model_name='testsuite',
            name='callfunc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.callfunc'),
        ),
    ]