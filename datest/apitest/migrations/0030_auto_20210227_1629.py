# Generated by Django 3.1.7 on 2021-02-27 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0029_testcase_runbefore'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testcase',
            old_name='runbefore',
            new_name='beforecase',
        ),
    ]