# Generated by Django 3.1.7 on 2021-02-28 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0036_testsuite_setupfunc'),
    ]

    operations = [
        migrations.AddField(
            model_name='testreport',
            name='errors',
            field=models.TextField(max_length=10000, null=True),
        ),
    ]