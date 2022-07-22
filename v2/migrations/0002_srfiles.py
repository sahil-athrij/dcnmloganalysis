# Generated by Django 3.1.2 on 2021-05-03 22:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('v2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SRFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fileId', models.CharField(max_length=200)),
                ('fileName', models.CharField(max_length=200)),
                ('fileContentType', models.CharField(max_length=200)),
                ('sr_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='v2.sr')),
            ],
        ),
    ]