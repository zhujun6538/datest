# Generated by Django 3.1.7 on 2021-02-27 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0028_baseurl_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcase',
            name='runbefore',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apitest.testcase'),
        ),
    ]