# Generated by Django 3.1.7 on 2021-02-25 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0013_auto_20210225_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reqquestval',
            name='type',
            field=models.CharField(choices=[('str', 'string'), ('int', 'int'), ('bool', 'bool')], default='str', max_length=10, verbose_name='类型'),
        ),
    ]
