# Generated by Django 3.1.7 on 2021-04-01 07:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apitest', '0070_auto_20210331_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='api',
            name='creater',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='apigroup',
            name='creater',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='project',
            name='creater',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='testbatch',
            name='creater',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='testcase',
            name='creater',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='testcasegroup',
            name='creater',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
    ]
