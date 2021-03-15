# Generated by Django 3.1.7 on 2021-02-25 06:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0003_testcase_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='Headerkey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Headerval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='HeaderParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('paramkey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.reqquestkey')),
                ('paramval', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.reqquestval')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testcase')),
            ],
        ),
    ]