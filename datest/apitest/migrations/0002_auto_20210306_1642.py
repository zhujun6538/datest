# Generated by Django 3.1.7 on 2021-03-06 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Formdatakey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Formdataval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('str', 'string'), ('int', 'int'), ('True', 'True'), ('False', 'False')], default='str', max_length=10, verbose_name='类型')),
            ],
        ),
        migrations.AlterField(
            model_name='api',
            name='header',
            field=models.ManyToManyField(blank=True, related_name='header_apis', to='apitest.Header', verbose_name='请求头'),
        ),
        migrations.AlterField(
            model_name='testsuite',
            name='args',
            field=models.ManyToManyField(blank=True, related_name='Argument_suites', to='apitest.Argument', verbose_name='pytest运行参数'),
        ),
        migrations.AlterField(
            model_name='testsuite',
            name='case',
            field=models.ManyToManyField(blank=True, related_name='case_suites', to='apitest.Testcase', verbose_name='用例集'),
        ),
        migrations.CreateModel(
            name='FormdataParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=1000, null=True, verbose_name='描述')),
                ('paramkey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.formdatakey', verbose_name='参数')),
                ('paramval', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.formdataval', verbose_name='值')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testcase')),
            ],
            options={
                'verbose_name_plural': 'FORMDATA参数',
            },
        ),
    ]