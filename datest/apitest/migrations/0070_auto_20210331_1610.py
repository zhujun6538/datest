# Generated by Django 3.1.7 on 2021-03-31 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0069_auto_20210331_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='api',
            name='jsonschema',
            field=models.TextField(blank=True, max_length=10000, null=True, verbose_name='jsonschema'),
        ),
        migrations.AlterField(
            model_name='api',
            name='description',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='描述'),
        ),
    ]