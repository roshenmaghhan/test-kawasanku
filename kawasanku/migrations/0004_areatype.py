# Generated by Django 3.2.13 on 2022-05-26 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kawasanku', '0003_jitter'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.JSONField()),
            ],
        ),
    ]
