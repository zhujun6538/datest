# Generated by Django 3.1.7 on 2021-04-01 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0073_auto_20210401_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='api',
            name='requesttype',
            field=models.CharField(choices=[('1', '异步'), ('2', '同步')], max_length=10, verbose_name='requesttype'),
        ),
    ]