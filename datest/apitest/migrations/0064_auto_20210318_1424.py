# Generated by Django 3.1.7 on 2021-03-18 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0063_auto_20210312_1156'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testbatch',
            old_name='batchno',
            new_name='name',
        ),
        migrations.AddField(
            model_name='testbatch',
            name='args',
            field=models.ManyToManyField(blank=True, related_name='Argument_batch', to='apitest.Argument', verbose_name='pytest运行参数'),
        ),
        migrations.AddField(
            model_name='testbatch',
            name='reruns',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='失败重跑次数'),
        ),
        migrations.AddField(
            model_name='testbatch',
            name='reruns_delay',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='重跑间隔时间'),
        ),
        migrations.AddField(
            model_name='testreport',
            name='testbatch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.testbatch', verbose_name='所属批次'),
        ),
        migrations.AlterField(
            model_name='debugtalk',
            name='content',
            field=models.TextField(blank=True, max_length=10000, null=True, verbose_name='内容'),
        ),
        migrations.AlterField(
            model_name='debugtalk',
            name='file',
            field=models.CharField(max_length=100, verbose_name='文件地址'),
        ),
        migrations.AlterField(
            model_name='debugtalk',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='apitest.project', verbose_name='项目'),
        ),
    ]
