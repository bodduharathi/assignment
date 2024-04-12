# Generated by Django 4.2.11 on 2024-04-09 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_id', models.IntegerField()),
                ('day_of_week', models.IntegerField()),
                ('start_time_local', models.TimeField()),
                ('end_time_local', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='StoreTimezone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_id', models.IntegerField()),
                ('timezone_str', models.CharField(max_length=50)),
            ],
        ),
    ]