# Generated by Django 3.1.7 on 2021-03-17 15:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Api',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updatetime', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('createtime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('DELETE', 'DELETE')], max_length=10, verbose_name='请求方法')),
                ('description', models.TextField(max_length=1000, verbose_name='描述')),
                ('isValid', models.BooleanField(default=True, verbose_name='是否有效')),
                ('url', models.CharField(max_length=100)),
                ('creater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
            ],
            options={
                'verbose_name_plural': '接口名称',
            },
        ),
        migrations.CreateModel(
            name='Argument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Assertkey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Assertval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(max_length=100000)),
                ('type', models.CharField(choices=[('str', 'string'), ('int', 'int'), ('True', 'True'), ('False', 'False')], default='str', max_length=10, verbose_name='类型')),
            ],
        ),
        migrations.CreateModel(
            name='BASEURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='环境')),
                ('url', models.CharField(max_length=100, verbose_name='url')),
            ],
            options={
                'verbose_name_plural': '测试环境',
            },
        ),
        migrations.CreateModel(
            name='CALLFUNC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
            ],
            options={
                'verbose_name_plural': 'call调用方法',
            },
        ),
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
        migrations.CreateModel(
            name='FUNC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
            ],
            options={
                'verbose_name_plural': 'setup调用方法',
            },
        ),
        migrations.CreateModel(
            name='Header',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=1000)),
            ],
            options={
                'verbose_name_plural': '请求头',
            },
        ),
        migrations.CreateModel(
            name='Headerkey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Headerval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Jenkinsreport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testno', models.IntegerField()),
                ('url', models.URLField(max_length=100, null=True)),
                ('result', models.CharField(choices=[('Y', '成功'), ('N', '失败')], max_length=10, null=True, verbose_name='运行结果')),
                ('output', models.TextField(max_length=10000, null=True)),
            ],
            options={
                'verbose_name_plural': 'Jenkins测试结果',
            },
        ),
        migrations.CreateModel(
            name='Postdata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apiurl', models.CharField(max_length=100)),
                ('reqdata', models.CharField(max_length=100, null=True)),
                ('repdata', models.CharField(max_length=10000, null=True)),
                ('reqtime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updatetime', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('createtime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=100)),
                ('banben', models.CharField(max_length=100, null=True)),
                ('creater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('sonpj', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.project')),
            ],
            options={
                'verbose_name_plural': '测试项目',
            },
        ),
        migrations.CreateModel(
            name='Reqquestkey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Reqquestval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('str', 'string'), ('int', 'int'), ('True', 'True'), ('False', 'False')], default='str', max_length=10, verbose_name='类型')),
            ],
        ),
        migrations.CreateModel(
            name='Testcase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updatetime', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('createtime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('caseno', models.CharField(max_length=100, verbose_name='用例编号')),
                ('casename', models.CharField(max_length=100, verbose_name='用例名称')),
                ('isValid', models.BooleanField(default=True, verbose_name='是否有效')),
                ('datamode', models.CharField(choices=[('JSON', 'JSON'), ('FORM-DATA', 'FORM-DATA')], max_length=10, verbose_name='请求参数类型')),
                ('requestdata', models.TextField(blank=True, default='{}', max_length=1000, null=True, verbose_name='请求报文')),
                ('responsedata', models.TextField(blank=True, max_length=10000, null=True, verbose_name='响应报文')),
                ('runtime', models.DateTimeField(blank=True, null=True, verbose_name='运行时间')),
                ('api', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.api', verbose_name='测试接口')),
                ('baseurl', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.baseurl', verbose_name='环境地址')),
                ('beforecase', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.testcase')),
                ('callfunc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.callfunc', verbose_name='自定义运行方法')),
                ('creater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
            ],
            options={
                'verbose_name_plural': '测试用例',
            },
        ),
        migrations.CreateModel(
            name='TESTSUITE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updatetime', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('createtime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=100, verbose_name='套件名称')),
                ('sleeptime', models.IntegerField(default=0, verbose_name='运行延时')),
                ('runtime', models.DateTimeField(null=True, verbose_name='运行时间')),
                ('reruns', models.IntegerField(blank=True, default=0, null=True, verbose_name='失败重跑次数')),
                ('reruns_delay', models.IntegerField(blank=True, default=0, null=True, verbose_name='重跑间隔时间')),
                ('isorder', models.BooleanField(default=False, verbose_name='是否顺序执行')),
                ('args', models.ManyToManyField(blank=True, related_name='Argument_suites', to='apitest.Argument', verbose_name='pytest运行参数')),
                ('baseurl', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.baseurl', verbose_name='环境地址')),
                ('callfunc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.callfunc', verbose_name='自定义运行方法')),
                ('case', models.ManyToManyField(blank=True, related_name='case_suites', to='apitest.Testcase', verbose_name='用例集')),
                ('creater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.project', verbose_name='所属项目')),
                ('setupfunc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.func', verbose_name='请求前置方法')),
            ],
            options={
                'verbose_name_plural': '测试套件',
            },
        ),
        migrations.CreateModel(
            name='TESTREPORT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reportname', models.CharField(max_length=100, verbose_name='报告名称')),
                ('testtime', models.DateTimeField(auto_now_add=True, verbose_name='测试时间')),
                ('testnum', models.IntegerField(verbose_name='用例数量')),
                ('result', models.CharField(choices=[('Y', '成功'), ('N', '失败')], max_length=10, verbose_name='运行结果')),
                ('suc', models.IntegerField(blank=True, null=True, verbose_name='成功用例数量')),
                ('fail', models.IntegerField(blank=True, null=True, verbose_name='失败用例数量')),
                ('file', models.FileField(default='report/html/index.html', upload_to='report', verbose_name='报告文件')),
                ('errors', models.TextField(max_length=10000, null=True, verbose_name='异常信息')),
                ('failcase', models.ManyToManyField(blank=True, related_name='case_failcase', to='apitest.Testcase', verbose_name='失败用例')),
                ('runner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='运行人')),
                ('succase', models.ManyToManyField(blank=True, related_name='case_succase', to='apitest.Testcase', verbose_name='成功用例')),
                ('testcases', models.ManyToManyField(related_name='case_report', to='apitest.Testcase', verbose_name='测试用例')),
                ('testsuite', models.ManyToManyField(related_name='suite_report', to='apitest.TESTSUITE', verbose_name='测试套件')),
            ],
            options={
                'verbose_name_plural': '测试报告',
            },
        ),
        migrations.CreateModel(
            name='Testcaselist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('runno', models.IntegerField(verbose_name='顺序号')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testcase', verbose_name='测试用例')),
                ('testsuite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testsuite', verbose_name='测试套件')),
            ],
            options={
                'verbose_name_plural': '顺序运行用例',
            },
        ),
        migrations.CreateModel(
            name='TestcaseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updatetime', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('createtime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=100)),
                ('creater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.project')),
            ],
            options={
                'verbose_name_plural': '用例分组',
            },
        ),
        migrations.AddField(
            model_name='testcase',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.testcasegroup', verbose_name='所属分组'),
        ),
        migrations.AddField(
            model_name='testcase',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.project', verbose_name='所属项目'),
        ),
        migrations.AddField(
            model_name='testcase',
            name='setupfunc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.func', verbose_name='请求前置方法'),
        ),
        migrations.CreateModel(
            name='Testbatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updatetime', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('createtime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('batchno', models.CharField(max_length=100)),
                ('runtime', models.DateTimeField(null=True)),
                ('creater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('testsuite', models.ManyToManyField(related_name='TESTSUITE_batch', to='apitest.TESTSUITE')),
            ],
            options={
                'verbose_name_plural': '测试批次',
            },
        ),
        migrations.CreateModel(
            name='Runparam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('param', models.CharField(max_length=100, verbose_name='参数')),
                ('description', models.TextField(max_length=100000, null=True, verbose_name='描述')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testcase')),
            ],
            options={
                'verbose_name_plural': '响应保存',
            },
        ),
        migrations.CreateModel(
            name='RequestParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=1000, null=True, verbose_name='描述')),
                ('paramkey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.reqquestkey', verbose_name='参数')),
                ('paramval', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.reqquestval', verbose_name='值')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testcase')),
            ],
            options={
                'verbose_name_plural': '请求参数',
            },
        ),
        migrations.CreateModel(
            name='HeaderParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=1000, null=True, verbose_name='描述')),
                ('paramkey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.headerkey', verbose_name='参数')),
                ('paramval', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.headerval', verbose_name='值')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testcase')),
            ],
            options={
                'verbose_name_plural': '自定义请求头',
            },
        ),
        migrations.AddField(
            model_name='func',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.project'),
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
        migrations.CreateModel(
            name='DebugTalk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(max_length=100, verbose_name='文件地址')),
                ('content', models.TextField(blank=True, max_length=10000, null=True, verbose_name='内容')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='apitest.project', verbose_name='项目')),
            ],
            options={
                'verbose_name_plural': '驱动py文件',
            },
        ),
        migrations.AddField(
            model_name='baseurl',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.project'),
        ),
        migrations.CreateModel(
            name='AssertParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=1000, null=True, verbose_name='描述')),
                ('mode', models.CharField(choices=[('assert_equal', 'equils'), ('assert_contains', 'contains'), ('assert_regex_match', 'regex_match')], default='eq', max_length=100, verbose_name='模式')),
                ('paramkey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.assertkey', verbose_name='参数')),
                ('paramval', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.assertval', verbose_name='值')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apitest.testcase')),
            ],
            options={
                'verbose_name_plural': '校验参数',
            },
        ),
        migrations.CreateModel(
            name='ApiGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updatetime', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('createtime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=100)),
                ('creater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.project')),
            ],
            options={
                'verbose_name_plural': '接口分组',
            },
        ),
        migrations.AddField(
            model_name='api',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.apigroup', verbose_name='所属分组'),
        ),
        migrations.AddField(
            model_name='api',
            name='header',
            field=models.ManyToManyField(blank=True, related_name='header_apis', to='apitest.Header', verbose_name='请求头'),
        ),
        migrations.AddField(
            model_name='api',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.project', verbose_name='所属项目'),
        ),
    ]
