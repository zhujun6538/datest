# Generated by Django 3.1.7 on 2021-02-26 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0017_auto_20210226_1000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testsuite',
            name='case',
            field=models.ManyToManyField(blank=True, null=True, related_name='case_suites', to='apitest.Testcase'),
        ),
    ]
