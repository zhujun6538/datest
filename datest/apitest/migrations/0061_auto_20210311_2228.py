# Generated by Django 3.1.7 on 2021-03-11 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0060_debugtalk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debugtalk',
            name='file',
            field=models.CharField(max_length=100),
        ),
    ]
