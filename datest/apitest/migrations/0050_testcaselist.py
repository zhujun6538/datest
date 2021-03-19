# Generated by Django 3.1.7 on 2021-03-03 05:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0049_auto_20210302_1805'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testcaselist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('runno', models.IntegerField()),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testcase')),
                ('testsuite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testsuite')),
            ],
            options={
                'verbose_name_plural': '运行用例',
            },
        ),
    ]