# Generated by Django 3.1.7 on 2021-03-02 03:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0046_auto_20210302_1121'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testbatch',
            options={'verbose_name_plural': '测试批次'},
        ),
        migrations.RenameField(
            model_name='testbatch',
            old_name='batchobs',
            new_name='testsuite',
        ),
    ]