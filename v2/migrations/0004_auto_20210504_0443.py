# Generated by Django 3.1.2 on 2021-05-03 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v2', '0003_auto_20210504_0441'),
    ]

    operations = [
        migrations.AddField(
            model_name='srfiles',
            name='id',
            field=models.AutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='srfiles',
            name='fileId',
            field=models.CharField(max_length=200),
        ),
    ]
